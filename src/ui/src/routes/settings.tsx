import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../auth/AuthProvider'
import { RequireAuth } from '../auth/RequireAuth'
import { getMe, patchMe } from '../api/me'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FormField } from '../components/ui/FormField'
import { TimezoneSelect } from '../components/TimezoneSelect'

const schema = z.object({
  display_name: z.string().min(1, 'Required').max(100),
  unit_system: z.enum(['imperial', 'metric']),
  timezone: z.string().min(1, 'Required'),
})
type FormData = z.infer<typeof schema>

function SettingsForm() {
  const { user } = useAuth()
  const token = user?.access_token ?? ''
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: () => getMe(token),
    enabled: !!token,
  })

  const mutation = useMutation({
    mutationFn: (values: FormData) => patchMe(token, values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  useEffect(() => {
    if (data) {
      reset({
        display_name: data.display_name,
        unit_system: data.unit_system,
        timezone: data.timezone,
      })
    }
  }, [data, reset])

  if (isLoading) return <div className="text-zinc-400">Loading…</div>

  return (
    <form
      onSubmit={(e) => void handleSubmit((v) => mutation.mutate(v))(e)}
      className="flex max-w-sm flex-col gap-4"
    >
      <FormField label="Display name" error={errors.display_name?.message}>
        <Input {...register('display_name')} />
      </FormField>
      <FormField label="Units" error={errors.unit_system?.message}>
        <select
          {...register('unit_system')}
          className="h-9 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-white"
        >
          <option value="imperial">Imperial (inches)</option>
          <option value="metric">Metric (mm)</option>
        </select>
      </FormField>
      <FormField label="Timezone" error={errors.timezone?.message}>
        <TimezoneSelect
          value={data?.timezone ?? 'UTC'}
          onChange={(tz) => reset({ ...watch(), timezone: tz })}
        />
      </FormField>
      {mutation.isError && (
        <p className="text-sm text-red-400">{String(mutation.error)}</p>
      )}
      {saved && <p className="text-sm text-green-400">Saved.</p>}
      <Button type="submit" disabled={isSubmitting || mutation.isPending}>
        Save
      </Button>
    </form>
  )
}

export default function SettingsPage() {
  return (
    <RequireAuth>
      <div className="min-h-screen bg-zinc-950 p-6 text-white">
        <h1 className="mb-6 text-xl font-bold">Profile Settings</h1>
        <SettingsForm />
      </div>
    </RequireAuth>
  )
}
