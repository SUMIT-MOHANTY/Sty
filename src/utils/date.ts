/**
 * Formats a date string to a more readable format
 * @param dateString - ISO date string or Date object
 * @returns Formatted date string (e.g., "Jan 5, 2023")
 */
export const formatDate = (dateString: string | Date): string => {
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Formats time from 24-hour format to 12-hour format with AM/PM
 * @param time - Time string in 24-hour format (e.g., "14:30")
 * @returns Formatted time string (e.g., "2:30 PM")
 */
export const formatTime = (time: string): string => {
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const hour12 = hours % 12 || 12;
  return `${hour12}:${minutes.toString().padStart(2, '0')} ${period}`;
};

/**
 * Gets an array of dates for the current week
 * @returns Array of Date objects for each day of the current week
 */
export const getCurrentWeekDates = (): Date[] => {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0 = Sunday, 6 = Saturday
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - dayOfWeek);

  return Array(7).fill(null).map((_, index) => {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + index);
    return date;
  });
};

/**
 * Checks if two dates are the same day
 * @param date1 - First date
 * @param date2 - Second date
 * @returns Boolean indicating if dates are the same day
 */
export const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};
