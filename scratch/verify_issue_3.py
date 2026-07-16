import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import SQLModel, create_engine, Session, select
from app.models.base_models import User, Printer, PrintProject, ProjectStatus, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.crud.crud_project import project as crud_project

def run_verification():
    # Use an in-memory SQLite database for testing
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    # Create tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created in memory.")

    with Session(engine) as db:
        # 1. Create a dummy User
        user = User(username="testuser", hashed_password="hashedpassword", role=UserRole.USER)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: id={user.id}, username={user.username}")

        # 2. Create a dummy Printer
        printer1 = Printer(name="P2S Living Room", type="P1S", connection_info="192.168.1.100", location="Living Room")
        printer2 = Printer(name="X2D Office", type="X1C", connection_info="192.168.1.101", location="Office")
        db.add(printer1)
        db.add(printer2)
        db.commit()
        db.refresh(printer1)
        db.refresh(printer2)
        print(f"Created printers: {printer1.name} (id={printer1.id}), {printer2.name} (id={printer2.id})")

        # 3. Create a PrintProject with printer1 associated
        project_in = ProjectCreate(
            name="Test Benchy",
            description="A test 3D print",
            status=ProjectStatus.IDEA,
            printer_id=printer1.id
        )

        # We can use our CRUD class to create
        created_project = crud_project.create_with_creator(db, obj_in=project_in, creator_id=user.id)
        print(f"Created project: id={created_project.id}, name={created_project.name}, printer_id={created_project.printer_id}")

        # Assert printer_id is correct
        assert created_project.printer_id == printer1.id, f"Expected printer_id {printer1.id}, got {created_project.printer_id}"

        # 4. Read the project back and check relationship
        db.expire_all() # Ensure we fetch fresh from DB
        db_project = db.exec(select(PrintProject).where(PrintProject.id == created_project.id)).one()
        print(f"Fetched project: name={db_project.name}, printer_id={db_project.printer_id}, associated printer={db_project.printer.name if db_project.printer else None}")

        assert db_project.printer is not None
        assert db_project.printer.id == printer1.id

        # 5. Update the project to associate with printer2
        project_up = ProjectUpdate(printer_id=printer2.id)
        updated_project = crud_project.update(db, db_obj=db_project, obj_in=project_up)
        print(f"Updated project: printer_id={updated_project.printer_id}")

        assert updated_project.printer_id == printer2.id, f"Expected printer_id {printer2.id}, got {updated_project.printer_id}"

        # Verify relationship updated
        db.expire_all()
        db_project_updated = db.exec(select(PrintProject).where(PrintProject.id == created_project.id)).one()
        print(f"Fetched updated project: associated printer={db_project_updated.printer.name if db_project_updated.printer else None}")

        assert db_project_updated.printer is not None
        assert db_project_updated.printer.id == printer2.id

        # 6. Dissociate the printer (set to None)
        project_up_none = ProjectUpdate(printer_id=None)
        dissociated_project = crud_project.update(db, db_obj=db_project_updated, obj_in=project_up_none)
        print(f"Dissociated project: printer_id={dissociated_project.printer_id}")

        assert dissociated_project.printer_id is None
        assert dissociated_project.printer is None

        print("\nAll verification checks passed successfully!")

if __name__ == "__main__":
    run_verification()
