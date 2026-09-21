import { useEffect, useState } from 'react';

/**
 * Відкладає значення на кілька сотень мілісекунд.
 *
 * Потрібно для пошуку: поки користувач друкує, запит на сервер не летить
 * після кожної літери.
 */
export function useDebouncedValue<T>(value: T, delayMs = 400): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
