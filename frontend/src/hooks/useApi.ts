import { API_BASE_URL } from "@/utils/constants";

type FetchOptions = RequestInit & { json?: unknown };

export async function apiFetch<TResponse>(
  path: string,
  options: FetchOptions = {}
): Promise<TResponse> {
  const { json, headers, ...rest } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...headers
    },
    body: json !== undefined ? JSON.stringify(json) : options.body,
    ...rest
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await response.json()) as TResponse;
  }

  return undefined as TResponse;
}
