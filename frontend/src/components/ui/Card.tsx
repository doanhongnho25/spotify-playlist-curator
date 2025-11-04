import { clsx } from "clsx";
import type { PropsWithChildren } from "react";

interface CardProps extends PropsWithChildren {
  className?: string;
  title?: string;
  description?: string;
  actions?: React.ReactNode;
}

export const Card = ({
  children,
  className,
  title,
  description,
  actions
}: CardProps) => (
  <div
    className={clsx(
      "rounded-2xl border border-white/10 bg-white/5/50 bg-opacity-40 p-6 shadow-xl shadow-black/20 backdrop-blur-sm",
      className
    )}
  >
    {(title || description || actions) && (
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          {title ? (
            <h3 className="text-lg font-semibold tracking-tight text-white">
              {title}
            </h3>
          ) : null}
          {description ? (
            <p className="text-sm text-white/60">{description}</p>
          ) : null}
        </div>
        {actions}
      </div>
    )}
    {children}
  </div>
);
