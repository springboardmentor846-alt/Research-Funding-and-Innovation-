import api from "./axios";

export async function getAdminOverview() {
  const response = await api.get("/admin/overview");
  return response.data;
}

export async function getAdminUsers(params = {}) {
  const response = await api.get("/admin/users", { params });
  return response.data;
}

export async function updateAdminUserStatus(userId, isActive) {
  const response = await api.patch(
    `/admin/users/${userId}/status`,
    { is_active: isActive }
  );
  return response.data;
}

export async function updateAdminUserRole(userId, role) {
  const response = await api.patch(
    `/admin/users/${userId}/role`,
    { role }
  );
  return response.data;
}
