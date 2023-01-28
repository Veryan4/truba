import { tokenService } from "./token.service";
import { routerService } from "./router.service";
import { userStore } from "./user.store";

export const httpService = {
  get,
  put,
  post,
  patch,
  del,
};

function baseHttp<T>(url: string, options?: RequestInit): Promise<T> {
  return fetch(url, options).then((response) => {
    if (response.status == 401 || response.status == 403) {
      userStore.setUser(null);
      tokenService.removeToken();
      routerService.navigate("/login");
      throw new Error("Unauthorized");
    }

    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json();
  });
}

function get<T>(url: string): Promise<T> {
  return baseHttp(url, {
    method: "GET",
    headers: createHeaders(),
  });
}

function put<T>(url: string, data: any | FormData): Promise<T> {
  const isFormData = data instanceof FormData;
  return baseHttp(url, {
    method: "PUT",
    headers: createHeaders(isFormData),
    body: createBody(data, isFormData),
  });
}

function post<T>(url: string, data: any): Promise<T> {
  const isFormData = data instanceof FormData;
  return baseHttp(url, {
    method: "POST",
    headers: createHeaders(isFormData),
    body: createBody(data, isFormData),
  });
}

function patch<T>(url: string, data: any | FormData): Promise<T> {
  const isFormData = data instanceof FormData;
  return baseHttp(url, {
    method: "PATCH",
    headers: createHeaders(isFormData),
    body: createBody(data, isFormData),
  });
}

function del<T>(url: string): Promise<T> {
  return baseHttp(url, {
    method: "DELETE",
    headers: createHeaders(),
  });
}

function createHeaders(isFormData?: boolean) {
  const headers: any = {
    Accept: "application/json",
    "Content-Type": isFormData
      ? "application/x-www-form-urlencoded"
      : "application/json",
  };
  const token = tokenService.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

function createBody(data: any, isFormData: boolean) {
  return isFormData ? new URLSearchParams(data as any) : JSON.stringify(data);
}
