import { forwardRef } from 'react'

const US_STATES = [
  ['AL', 'Alabama'], ['AK', 'Alaska'], ['AZ', 'Arizona'], ['AR', 'Arkansas'],
  ['CA', 'California'], ['CO', 'Colorado'], ['CT', 'Connecticut'], ['DE', 'Delaware'],
  ['FL', 'Florida'], ['GA', 'Georgia'], ['HI', 'Hawaii'], ['ID', 'Idaho'],
  ['IL', 'Illinois'], ['IN', 'Indiana'], ['IA', 'Iowa'], ['KS', 'Kansas'],
  ['KY', 'Kentucky'], ['LA', 'Louisiana'], ['ME', 'Maine'], ['MD', 'Maryland'],
  ['MA', 'Massachusetts'], ['MI', 'Michigan'], ['MN', 'Minnesota'], ['MS', 'Mississippi'],
  ['MO', 'Missouri'], ['MT', 'Montana'], ['NE', 'Nebraska'], ['NV', 'Nevada'],
  ['NH', 'New Hampshire'], ['NJ', 'New Jersey'], ['NM', 'New Mexico'], ['NY', 'New York'],
  ['NC', 'North Carolina'], ['ND', 'North Dakota'], ['OH', 'Ohio'], ['OK', 'Oklahoma'],
  ['OR', 'Oregon'], ['PA', 'Pennsylvania'], ['RI', 'Rhode Island'], ['SC', 'South Carolina'],
  ['SD', 'South Dakota'], ['TN', 'Tennessee'], ['TX', 'Texas'], ['UT', 'Utah'],
  ['VT', 'Vermont'], ['VA', 'Virginia'], ['WA', 'Washington'], ['WV', 'West Virginia'],
  ['WI', 'Wisconsin'], ['WY', 'Wyoming'], ['DC', 'District of Columbia'],
] as const

interface StateSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const StateSelect = forwardRef<HTMLSelectElement, StateSelectProps>(
  ({ className, ...props }, ref) => (
    <select
      ref={ref}
      className={
        'w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white ' +
        'placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-600 ' +
        (className ?? '')
      }
      {...props}
    >
      <option value="">— select state —</option>
      {US_STATES.map(([abbr, name]) => (
        <option key={abbr} value={abbr}>
          {abbr} – {name}
        </option>
      ))}
    </select>
  ),
)
StateSelect.displayName = 'StateSelect'
