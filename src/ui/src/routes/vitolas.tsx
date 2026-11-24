import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../auth/AuthProvider'
import { RequireAuth } from '../auth/RequireAuth'
import { AppLayout } from '../components/AppLayout'
import { Modal } from '../components/ui/Modal'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FormField } from '../components/ui/FormField'
import { getMe } from '../api/me'
import { getVitolas, createVitola, updateVitola, deleteVitola, type Vitola } from '../api/vitolas'

const schema = z.object({
  name: z.string().min(1, 'Required'),
  length_inches: z.string().optional(),
  ring_gauge: z.coerce.number().int().positive().optional().or(z.literal('')),
})
type FormData = z.infer<typeof schema>

function VitolaForm({
  initial,
  token,
  onDone,
}: {
  initial?: Vitola
  token: string
  onDone: () => void
}) {
  const queryClient = useQueryClient()

  const save = useMutation({
    mutationFn: (data: FormData) => {
      const payload = {
        name: data.name,
        length_inches: data.length_inches || undefined,
        ring_gauge: data.ring_gauge === '' ? undefined : data.ring_gauge as number | undefined,
      }
      return initial ? updateVitola(token, initial.id, payload) : createVitola(token, payload)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['vitolas'] })
      onDone()
    },
  })

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? '',
      length_inches: initial?.length_inches ?? '',
      ring_gauge: initial?.ring_gauge ?? '',
    },
  })

  return (
    <form onSubmit={(e) => void handleSubmit((v) => save.mutate(v))(e)} className="flex flex-col gap-4">
      <FormField label="Name *" error={errors.name?.message}>
        <Input {...register('name')} autoFocus />
      </FormField>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Length (inches)" error={errors.length_inches?.message}>
          <Input {...register('length_inches')} placeholder="e.g. 5.00" />
        </FormField>
        <FormField label="Ring Gauge" error={errors.ring_gauge?.message}>
          <Input {...register('ring_gauge')} type="number" placeholder="e.g. 50" />
        </FormField>
      </div>
      {save.isError && (
        <p className="text-sm text-red-400">{String(save.error)}</p>
      )}
      <div className="flex justify-end gap-2 pt-1">
        <Button type="button" onClick={onDone} className="bg-zinc-700 hover:bg-zinc-600">
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting || save.isPending}>
          {initial ? 'Save changes' : 'Create vitola'}
        </Button>
      </div>
    </form>
  )
}

function VitolasContent() {
  const { user } = useAuth()
  const token = user?.access_token ?? ''
  const queryClient = useQueryClient()

  const { data: me } = useQuery({
    queryKey: ['me'],
    queryFn: () => getMe(token),
    enabled: !!token,
  })
  const isAdmin = me?.role === 'admin'

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Vitola | undefined>(undefined)
  const [confirmDelete, setConfirmDelete] = useState<Vitola | undefined>(undefined)

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('new') === '1') {
      setEditing(undefined)
      setModalOpen(true)
      window.history.replaceState(null, '', '/vitolas')
    }
  }, [])

  const { data: vitolas = [], isLoading } = useQuery({
    queryKey: ['vitolas'],
    queryFn: () => getVitolas(token),
    enabled: !!token,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteVitola(token, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['vitolas'] })
      setConfirmDelete(undefined)
    },
  })

  function openCreate() {
    setEditing(undefined)
    setModalOpen(true)
  }

  function openEdit(vitola: Vitola) {
    setEditing(vitola)
    setModalOpen(true)
  }

  function closeModal() {
    setModalOpen(false)
    setEditing(undefined)
  }

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold">Vitolas</h1>
        {isAdmin && (
          <Button onClick={openCreate}>+ New vitola</Button>
        )}
      </div>

      {isLoading ? (
        <p className="text-zinc-400">Loading…</p>
      ) : vitolas.length === 0 ? (
        <p className="text-zinc-500">No vitolas yet.{isAdmin ? ' Create one above.' : ''}</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-700">
          <table className="w-full text-sm">
            <thead className="bg-zinc-800 text-left text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Length (in)</th>
                <th className="px-4 py-3 font-medium">Ring Gauge</th>
                {isAdmin && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {vitolas.map((vitola) => (
                <tr key={vitola.id} className="hover:bg-zinc-800/50">
                  <td className="px-4 py-3 font-medium text-white">{vitola.name}</td>
                  <td className="px-4 py-3 text-zinc-400">{vitola.length_inches ?? '—'}</td>
                  <td className="px-4 py-3 text-zinc-400">{vitola.ring_gauge ?? '—'}</td>
                  {isAdmin && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openEdit(vitola)}
                        className="mr-3 text-zinc-400 hover:text-white"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmDelete(vitola)}
                        className="text-zinc-400 hover:text-red-400"
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editing ? `Edit — ${editing.name}` : 'New vitola'}
        onClose={closeModal}
      >
        <VitolaForm key={editing?.id ?? 'new'} initial={editing} token={token} onDone={closeModal} />
      </Modal>

      <Modal
        open={!!confirmDelete}
        title="Delete vitola"
        onClose={() => setConfirmDelete(undefined)}
      >
        <p className="mb-5 text-zinc-300">
          Delete <span className="font-semibold text-white">{confirmDelete?.name}</span>? This cannot be undone.
        </p>
        {remove.isError && (
          <p className="mb-3 text-sm text-red-400">{String(remove.error)}</p>
        )}
        <div className="flex justify-end gap-2">
          <Button onClick={() => setConfirmDelete(undefined)} className="bg-zinc-700 hover:bg-zinc-600">
            Cancel
          </Button>
          <Button
            onClick={() => confirmDelete && remove.mutate(confirmDelete.id)}
            disabled={remove.isPending}
            className="bg-red-700 hover:bg-red-800"
          >
            Delete
          </Button>
        </div>
      </Modal>
    </>
  )
}

export default function VitolasPage() {
  return (
    <RequireAuth>
      <AppLayout>
        <VitolasContent />
      </AppLayout>
    </RequireAuth>
  )
}
