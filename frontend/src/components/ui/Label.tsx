import type { PropsWithChildren } from "react";
import { clsx } from "clsx";

interface LabelProps extends PropsWithChildren {
  htmlFor?: string;
  className?: string;
}

export const Label = ({ children, className, htmlFor }: LabelProps) => (
  <label
    className={clsx("text-sm font-medium text-white/80", className)}
    htmlFor={htmlFor}
  >
    {children}
  </label>
);
