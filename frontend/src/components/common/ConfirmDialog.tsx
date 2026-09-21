/** Діалог підтвердження для незворотних дій. */

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
} from '@mui/material';
import { useEffect, useState } from 'react';

import { t } from '@/i18n/uk';

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmColor?: 'primary' | 'error' | 'warning' | 'success';
  busy?: boolean;
  /** Показати поле коментаря і передати його в onConfirm. */
  withComment?: boolean;
  commentLabel?: string;
  onConfirm: (comment?: string) => void;
  onClose: () => void;
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = t.actionConfirm,
  cancelLabel = t.actionCancel,
  confirmColor = 'primary',
  busy = false,
  withComment = false,
  commentLabel,
  onConfirm,
  onClose,
}: ConfirmDialogProps) {
  const [comment, setComment] = useState('');

  useEffect(() => {
    if (open) setComment('');
  }, [open]);

  return (
    <Dialog open={open} onClose={busy ? undefined : onClose} fullWidth maxWidth="xs">
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        {description ? <DialogContentText>{description}</DialogContentText> : null}
        {withComment ? (
          <TextField
            sx={{ mt: 2 }}
            label={commentLabel}
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            multiline
            minRows={2}
            slotProps={{ htmlInput: { maxLength: 500 } }}
          />
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={busy}>
          {cancelLabel}
        </Button>
        <Button
          onClick={() => onConfirm(withComment ? comment.trim() || undefined : undefined)}
          color={confirmColor}
          variant="contained"
          disabled={busy}
        >
          {confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
