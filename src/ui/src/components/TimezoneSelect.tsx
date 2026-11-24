interface Props {
  value: string
  onChange: (tz: string) => void
  className?: string
}

// Common IANA timezones grouped by region
const TIMEZONES: Record<string, string[]> = {
  'Americas': [
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Phoenix',
    'America/Los_Angeles',
    'America/Anchorage',
    'Pacific/Honolulu',
    'America/Toronto',
    'America/Vancouver',
    'America/Mexico_City',
    'America/Bogota',
    'America/Lima',
    'America/Santiago',
    'America/Sao_Paulo',
    'America/Argentina/Buenos_Aires',
  ],
  'Europe': [
    'Europe/London',
    'Europe/Dublin',
    'Europe/Lisbon',
    'Europe/Paris',
    'Europe/Berlin',
    'Europe/Rome',
    'Europe/Madrid',
    'Europe/Amsterdam',
    'Europe/Brussels',
    'Europe/Zurich',
    'Europe/Stockholm',
    'Europe/Oslo',
    'Europe/Copenhagen',
    'Europe/Helsinki',
    'Europe/Warsaw',
    'Europe/Prague',
    'Europe/Vienna',
    'Europe/Budapest',
    'Europe/Bucharest',
    'Europe/Athens',
    'Europe/Istanbul',
    'Europe/Moscow',
  ],
  'Asia / Pacific': [
    'Asia/Dubai',
    'Asia/Kolkata',
    'Asia/Colombo',
    'Asia/Dhaka',
    'Asia/Bangkok',
    'Asia/Ho_Chi_Minh',
    'Asia/Jakarta',
    'Asia/Singapore',
    'Asia/Kuala_Lumpur',
    'Asia/Manila',
    'Asia/Shanghai',
    'Asia/Hong_Kong',
    'Asia/Taipei',
    'Asia/Seoul',
    'Asia/Tokyo',
    'Australia/Perth',
    'Australia/Adelaide',
    'Australia/Sydney',
    'Australia/Melbourne',
    'Pacific/Auckland',
  ],
  'Africa / Middle East': [
    'Africa/Cairo',
    'Africa/Johannesburg',
    'Africa/Lagos',
    'Africa/Nairobi',
    'Asia/Jerusalem',
    'Asia/Riyadh',
    'Asia/Kuwait',
    'Asia/Beirut',
    'Asia/Amman',
  ],
  'UTC': ['UTC'],
}

export function TimezoneSelect({ value, onChange, className }: Props) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={
        className ??
        'h-9 w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-white'
      }
    >
      {Object.entries(TIMEZONES).map(([group, zones]) => (
        <optgroup key={group} label={group}>
          {zones.map((tz) => (
            <option key={tz} value={tz}>
              {tz.replace(/_/g, ' ')}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  )
}
