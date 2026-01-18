import { format, parse, parseISO, isValid } from 'date-fns';

const DATE_ONLY_FORMAT = 'yyyy-MM-dd';

export const parsePuzzleDate = (dateValue) => {
  if (!dateValue) return null;

  if (typeof dateValue === 'string') {
    if (dateValue.includes('T')) {
      const parsed = parseISO(dateValue);
      return isValid(parsed) ? parsed : null;
    }

    const parsed = parse(dateValue, DATE_ONLY_FORMAT, new Date());
    return isValid(parsed) ? parsed : null;
  }

  const parsed = new Date(dateValue);
  return isValid(parsed) ? parsed : null;
};

export const formatPuzzleDate = (dateValue, displayFormat) => {
  const parsed = parsePuzzleDate(dateValue);
  if (!parsed) return '';
  return format(parsed, displayFormat);
};

export const getDateInputValue = (dateValue) => {
  if (!dateValue) return format(new Date(), DATE_ONLY_FORMAT);

  if (typeof dateValue === 'string') {
    if (dateValue.includes('T')) {
      const parsed = parseISO(dateValue);
      return isValid(parsed) ? format(parsed, DATE_ONLY_FORMAT) : '';
    }

    return dateValue;
  }

  const parsed = parsePuzzleDate(dateValue);
  return parsed ? format(parsed, DATE_ONLY_FORMAT) : '';
};

export const getTodayInputValue = () => format(new Date(), DATE_ONLY_FORMAT);

export const getPuzzleDateSortValue = (dateValue) => {
  const parsed = parsePuzzleDate(dateValue);
  return parsed ? parsed.getTime() : 0;
};
