export const formatDate = (value?: string | null) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric"
  });
};

export const formatRelativeDays = (value?: string | null) => {
  if (!value) return "—";
  const target = new Date(value).getTime();
  const now = Date.now();
  const diff = Math.round((target - now) / (1000 * 60 * 60 * 24));
  if (Number.isNaN(diff)) return "—";
  if (diff === 0) return "Today";
  if (diff > 0) return `${diff} day${diff === 1 ? "" : "s"}`;
  return `${Math.abs(diff)} day${diff === -1 ? "" : "s"} ago`;
};

export const formatNumber = (value?: number | null) => {
  if (value === undefined || value === null) return "—";
  return new Intl.NumberFormat().format(value);
};
