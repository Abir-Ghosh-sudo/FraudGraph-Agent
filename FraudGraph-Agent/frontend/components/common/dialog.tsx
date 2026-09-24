"use client";

import {
  useEffect,
  useRef,
  type ReactNode,
} from "react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/common/button";

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: ReactNode;
  footer?: ReactNode;
  className?: string;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  className,
  closeOnOverlayClick = true,
  closeOnEscape = true,
}: DialogProps) {
  const dialogRef =
    useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open || !closeOnEscape) {
      return;
    }

    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [open, closeOnEscape, onClose]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow = "hidden";

    const firstFocusable =
      dialogRef.current?.querySelector<
        HTMLElement
      >(
        "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])",
      );

    firstFocusable?.focus();

    return () => {
      document.body.style.overflow =
        previousOverflow;
    };
  }, [open]);

  if (!open) {
    return null;
  }

  const handleOverlayClick = (
    event: React.MouseEvent<HTMLDivElement>,
  ) => {
    if (
      closeOnOverlayClick &&
      event.target === event.currentTarget
    ) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-black/70 p-4"
      role="presentation"
      onMouseDown={handleOverlayClick}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="neo-dialog-title"
        aria-describedby={
          description
            ? "neo-dialog-description"
            : undefined
        }
        className={cn(
          "w-full max-w-xl",
          "border-[4px] border-black",
          "bg-[var(--surface)] text-black",
          "shadow-[10px_10px_0_#000]",
          "outline-none",
          className,
        )}
        onMouseDown={(event) =>
          event.stopPropagation()
        }
      >
        <div className="flex items-start justify-between gap-4 border-b-[4px] border-black bg-[var(--yellow)] p-4 sm:p-5">
          <div className="min-w-0">
            <h2
              id="neo-dialog-title"
              className="text-xl font-black uppercase leading-tight tracking-tight sm:text-2xl"
            >
              {title}
            </h2>

            {description && (
              <p
                id="neo-dialog-description"
                className="mt-2 text-sm font-bold leading-relaxed"
              >
                {description}
              </p>
            )}
          </div>

          <Button
            variant="dark"
            size="icon"
            aria-label="Close dialog"
            onClick={onClose}
          >
            <span
              aria-hidden="true"
              className="text-lg leading-none"
            >
              ×
            </span>
          </Button>
        </div>

        <div className="max-h-[65vh] overflow-y-auto p-4 sm:p-6">
          {children}
        </div>

        {footer && (
          <div className="flex flex-wrap items-center justify-end gap-3 border-t-[4px] border-black bg-white p-4 sm:p-5">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export interface ConfirmDialogProps
  extends Omit<
    DialogProps,
    "children" | "footer"
  > {
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?:
    | "primary"
    | "yellow"
    | "lime"
    | "pink"
    | "cyan"
    | "orange"
    | "danger"
    | "dark";
  loading?: boolean;
  onConfirm: () => void | Promise<void>;
}

export function ConfirmDialog({
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  confirmVariant = "danger",
  loading = false,
  onConfirm,
  onClose,
  ...props
}: ConfirmDialogProps) {
  return (
    <Dialog
      {...props}
      onClose={onClose}
      footer={
        <>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={loading}
          >
            {cancelLabel}
          </Button>

          <Button
            variant={confirmVariant}
            loading={loading}
            onClick={() => {
              void onConfirm();
            }}
          >
            {confirmLabel}
          </Button>
        </>
      }
    />
  );
}

export default Dialog;