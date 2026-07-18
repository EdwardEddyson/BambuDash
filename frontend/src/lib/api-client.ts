import axios from "axios";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "/api/v1").replace(/\/$/, "");

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to inject JWT token in Authorization headers
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor to handle session expirations / unauthenticated state
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
      }
    }
    return Promise.reject(error);
  }
);

// Auth helper functions
export const authApi = {
  login: async (username: string, password: string) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    const response = await apiClient.post("/auth/login", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data; // Expected response shape: { access_token: string, token_type: string }
  },

  register: async (username: string, email: string, fullName: string, password: string) => {
    const response = await apiClient.post("/users/", {
      username,
      email,
      full_name: fullName,
      password,
    });
    return response.data;
  },

  me: async () => {
    const response = await apiClient.get("/users/me");
    return response.data;
  },
};

export const projectsApi = {
  getAll: async () => {
    const response = await apiClient.get("/projects/");
    return response.data;
  },
  create: async (data: { name: string; description?: string; status?: string; image_stl_url?: string }) => {
    const response = await apiClient.post("/projects/", data);
    return response.data;
  },
  update: async (id: number, data: { name?: string; description?: string; status?: string; image_stl_url?: string }) => {
    const response = await apiClient.patch(`/projects/${id}`, data);
    return response.data;
  },
  addRequirement: async (projectId: number, requirement: { material_type: string; color_hex: string; estimated_consumption_g: number }) => {
    const response = await apiClient.post(`/projects/${projectId}/requirements`, requirement);
    return response.data;
  },
  checkFeasibility: async (projectId: number, spoolId: number) => {
    const response = await apiClient.get(`/projects/${projectId}/feasibility?filament_spool_id=${spoolId}`);
    return response.data;
  }
};

export const makerworldApi = {
  search: async (query: string) => {
    const response = await apiClient.get(`/makerworld/search?q=${encodeURIComponent(query)}`);
    return response.data;
  }
};

export const storeApi = {
  lookup: async (productSlug: string) => {
    const response = await apiClient.get(`/store/lookup/${productSlug}`);
    return response.data;
  }
};
