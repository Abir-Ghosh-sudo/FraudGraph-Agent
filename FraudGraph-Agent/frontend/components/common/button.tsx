import {
  forwardRef,
  type ButtonHTMLAttributes,
} from "react";

import { cn } from "@/lib/utils";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "yellow"
  | "lime"
  | "pink"
  | "cyan"
  | "orange"
  | "danger"
  | "dark"
  | "outline"
  | "ghost";

export type ButtonSize =
  | "sm"
  | "md"
  | "lg"
  | "icon";

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
}

const variantClasses: Record<
  ButtonVariant,
  string
> = {
  primary:
    "bg-[var(--yellow)] text-black hover:bg-[var(--lime)]",

  secondary:
    "bg-white text-black hover:bg-[var(--cyan)]",

  yellow:
    "bg-[var(--yellow)] text-black hover:bg-[var(--orange)]",

  lime:
    "bg-[var(--lime)] text-black hover:bg-[var(--yellow)]",

  pink:
    "bg-[var(--pink)] text-black hover:bg-[var(--yellow)]",

  cyan:
    "bg-[var(--cyan)] text-black hover:bg-[var(--lime)]",

  orange:
    "bg-[var(--orange)] text-black hover:bg-[var(--yellow)]",

  danger:
    "bg-[var(--red)] text-white hover:bg-[var(--pink)]",

  dark:
    "bg-black text-white hover:bg-[#242424]",

  outline:
    "bg-transparent text-black hover:bg-white",

  ghost:
    "border-transparent bg-transparent text-black shadow-none hover:bg-white",
};

const sizeClasses: Record<
  ButtonSize,
  string
> = {
  sm:
    "min-h-9 px-3 text-xs",

  md:
    "min-h-11 px-4 text-sm",

  lg:
    "min-h-13 px-6 text-base",

  icon:
    "h-11 w-11 p-0",
};

const Spinner = () => (
  <span
    aria-hidden="true"
    className="inline-block h-4 w-4 animate-spin border-[3px] border-current border-r-transparent"
  />
);

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonProps
>(function Button(
  {
    variant = "primary",
    size = "md",
    loading = false,
    disabled,
    className,
    children,
    type = "button",
    ...props
  },
  ref,
) {
  const isDisabled = disabled || loading;

  return (
    <button
      ref={ref}
      type={type}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={cn(
        "neo-button",
        "inline-flex items-center justify-center gap-2",
        "border-[3px] border-black",
        "font-black uppercase tracking-[0.02em]",
        "transition-none",
        "shadow-[4px_4px_0_#000]",
        "hover:translate-x-[2px]",
        "hover:translate-y-[2px]",
        "hover:shadow-[2px_2px_0_#000]",
        "active:translate-x-[4px]",
        "active:translate-y-[4px]",
        "active:shadow-none",
        "disabled:cursor-not-allowed",
        "disabled:opacity-50",
        "disabled:pointer-events-none",
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <>
          <Spinner />
          <span>Loading</span>
        </>
      ) : (
        children
      )}
    </button>
  );
});

Button.displayName = "Button";

export interface IconButtonProps
  extends Omit<
    ButtonProps,
    "size" | "children"
  > {
  label: string;
  children: React.ReactNode;
}

export function IconButton({
  label,
  children,
  className,
  ...props
}: IconButtonProps) {
  return (
    <Button
      {...props}
      size="icon"
      aria-label={label}
      title={label}
      className={className}
    >
      {children}
    </Button>
  );
}

export default Button;