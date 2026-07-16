
import enum
from typing import List, Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


# ---------------------------------
# Enums for Status and Roles
# ---------------------------------

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class FilamentStatus(str, enum.Enum):
    DRAFT = "draft"          # Automatically discovered, needs enrichment (price, owner)
    AVAILABLE = "available"  # Enriched and ready to use
    IN_USE = "in_use"        # Currently loaded in a printer
    SPENT = "spent"          # Used up

class ProjectStatus(str, enum.Enum):
    IDEA = "idea"
    PLANNED = "planned"
    PRINTING = "printing"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class OrderStatus(str, enum.Enum):
    PLANNING = "planning"    # Shopping cart phase
    ORDERED = "ordered"      # Order has been placed
    DELIVERED = "delivered"  # All items received

class SpoolType(str, enum.Enum):
    SPOOL = "spool"
    REFILL = "refill"


# ---------------------------------
# Link/Association Models
# ---------------------------------

class OrderItemSplit(SQLModel, table=True):
    """
    This is the core of the split-billing logic.
    It links an OrderItem to a User and defines the ownership percentage.
    """
    order_item_id: int = Field(foreign_key="orderitem.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    ownership_percentage: float = Field(default=1.0, ge=0.0, le=1.0, description="Ownership share, e.g., 0.5 for 50%")

    # Relationships to fetch the actual objects
    order_item: "OrderItem" = Relationship(back_populates="user_links")
    user: "User" = Relationship(back_populates="order_item_links")

class ProjectFilamentRequirement(SQLModel, table=True):
    """
    Links a project to the type and amount of filament it needs.
    This does NOT link to a specific spool, allowing for a "live check"
    against all available spools of the required type.
    """
    project_id: int = Field(foreign_key="printproject.id", primary_key=True)
    # Using descriptive fields instead of a FK to a "FilamentType" table for simplicity
    material_type: str = Field(primary_key=True)
    color_hex: str = Field(primary_key=True)

    estimated_consumption_g: float

    project: "PrintProject" = Relationship(back_populates="filament_requirements")


# ---------------------------------
# Core Data Models
# ---------------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # A user can own multiple filament spools
    owned_filaments: List["FilamentSpool"] = Relationship(back_populates="owner")

    # A user is part of multiple order item splits
    order_item_links: List[OrderItemSplit] = Relationship(back_populates="user")

    # A user can create multiple projects
    projects_created: List["PrintProject"] = Relationship(back_populates="creator")

class Printer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, description="e.g., 'P2S Living Room' or 'X2D Office'")
    type: str = Field(description="e.g., 'P1S', 'X1C'")
    # For local MQTT or cloud API connection
    connection_info: str = Field(description="IP Address for local, device_id for cloud etc.")
    location: Optional[str] = Field(default=None, nullable=True, description="Physical location")

    print_jobs: List["PrintJob"] = Relationship(back_populates="printer")

class FilamentSpool(SQLModel, table=True):
    """
    Represents a single, physical spool of filament.
    The "Enrichment" strategy is handled by the 'status' field.
    New spools from MQTT are created with status 'DRAFT'.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # Data from Bambu Ecosystem (MQTT/RFID)
    bambu_tray_id: Optional[str] = Field(default=None, index=True, description="UID from the Bambu AMS tray")
    material_type: str = Field(index=True, description="e.g., 'PLA', 'PETG', 'ABS'")
    color_hex: str = Field(description="HTML hex color code, e.g., '#FFFFFF'")
    remaining_weight_g: float = Field(description="Updated via MQTT from AMS")

    # Data added via "Enrichment" UI
    price: Optional[float] = Field(default=None, description="Price for this spool")
    spool_type: SpoolType = Field(default=SpoolType.SPOOL)
    status: FilamentStatus = Field(default=FilamentStatus.DRAFT, index=True)

    # Foreign key to the user who owns it. Can be null for communal filament.
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="owned_filaments")

    # Link to the order item this spool came from (optional)
    order_item_id: Optional[int] = Field(default=None, foreign_key="orderitem.id")
    order_item: Optional["OrderItem"] = Relationship(back_populates="resulting_spools")

    location: Optional[str] = Field(default=None, nullable=True, description="Physical location")
    product_slug: Optional[str] = Field(default=None, nullable=True)
    sku: Optional[str] = Field(default=None, nullable=True)
    variant_title: Optional[str] = Field(default=None, nullable=True)

    # A spool can be used in many print jobs
    print_jobs: List["PrintJob"] = Relationship(back_populates="filament_spool_used")

class PrintProject(SQLModel, table=True):
    """
    Represents a project, from idea to completion.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    status: ProjectStatus = Field(default=ProjectStatus.IDEA, index=True)
    image_stl_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    creator_id: int = Field(foreign_key="user.id")
    creator: User = Relationship(back_populates="projects_created")

    # M2M relationship for filament requirements
    filament_requirements: List[ProjectFilamentRequirement] = Relationship(back_populates="project")

    # A project can have multiple print jobs (e.g., re-prints or multi-part prints)
    print_jobs: List["PrintJob"] = Relationship(back_populates="project")

class PrintJob(SQLModel, table=True):
    """
    An actual instance of a print being run on a printer.
    This links a project to a specific filament spool and tracks consumption.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    # Can be linked to a project, but doesn't have to be (for ad-hoc prints)
    project_id: Optional[int] = Field(default=None, foreign_key="printproject.id")
    project: Optional[PrintProject] = Relationship(back_populates="print_jobs")

    printer_id: int = Field(foreign_key="printer.id")
    printer: Printer = Relationship(back_populates="print_jobs")

    filament_spool_used_id: int = Field(foreign_key="filamentspool.id")
    filament_spool_used: FilamentSpool = Relationship(back_populates="print_jobs")

    actual_consumption_g: Optional[float] = None

class Order(SQLModel, table=True):
    """
    A bulk order placed at a store.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    order_date: datetime = Field(default_factory=datetime.utcnow)
    store_name: str = Field(default="Bambu Lab Store")
    status: OrderStatus = Field(default=OrderStatus.PLANNING, index=True)

    # User who initiated the order planning
    creator_id: int = Field(foreign_key="user.id")

    # An order consists of multiple items
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    """
    A single line item within an order, e.g., '2x Bambu PLA Basic Black'.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    quantity: int = Field(default=1)
    price_per_unit: float
    product_slug: Optional[str] = Field(default=None, nullable=True)
    sku: Optional[str] = Field(default=None, nullable=True)
    variant_title: Optional[str] = Field(default=None, nullable=True)

    order_id: int = Field(foreign_key="order.id")
    order: Order = Relationship(back_populates="items")

    # M2M link to users defining who owns this item (and how much of it)
    user_links: List[OrderItemSplit] = Relationship(back_populates="order_item")

    # When an order is delivered, this can be linked to the physical spools created
    resulting_spools: List[FilamentSpool] = Relationship(back_populates="order_item")
