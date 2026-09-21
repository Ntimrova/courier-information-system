/** Форматування дат, чисел і телефонів для показу користувачу. */

const dateFormatter = new Intl.DateTimeFormat('uk-UA', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

const dateTimeFormatter = new Intl.DateTimeFormat('uk-UA', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

/** "2026-10-01" -> "01.10.2026" */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return dateFormatter.format(date);
}

/** ISO-мітка часу -> "01.10.2026, 14:35" */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return dateTimeFormatter.format(date);
}

/** "1.500" -> "1,5 кг" */
export function formatWeight(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return '-';
  const numeric = typeof value === 'number' ? value : Number.parseFloat(value);
  if (Number.isNaN(numeric)) return String(value);
  return `${numeric.toLocaleString('uk-UA', { maximumFractionDigits: 3 })} кг`;
}

/** Сьогоднішня дата у форматі, який приймає <input type="date">. */
export function todayAsInputValue(): string {
  const now = new Date();
  const offsetMinutes = now.getTimezoneOffset();
  const local = new Date(now.getTime() - offsetMinutes * 60_000);
  return local.toISOString().slice(0, 10);
}

/** Скорочує довгий текст, щоб таблиця не розповзалася. */
export function truncate(value: string, maxLength = 48): string {
  if (value.length <= maxLength) return value;
  return `${value.slice(0, maxLength - 1)}…`;
}
