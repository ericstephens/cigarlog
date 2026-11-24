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
import { getFactories, createFactory, updateFactory, deleteFactory, type Factory } from '../api/factories'

const schema = z.object({
  name: z.string().min(1, 'Required'),
  city: z.string().optional(),
  country: z.string().optional(),
  notes: z.string().optional(),
})
type FormData = z.infer<typeof schema>

function FactoryForm({
  initial,
  token,
  onDone,
}: {
  initial?: Factory
  token: string
  onDone: () => void
}) {
  const queryClient = useQueryClient()

  const save = useMutation({
    mutationFn: (data: FormData) =>
      initial ? updateFactory(token, initial.id, data) : createFactory(token, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['factories'] })
      onDone()
    },
  })

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? '',
      city: initial?.city ?? '',
      country: initial?.country ?? '',
      notes: initial?.notes ?? '',
    },
  })

  return (
    <form onSubmit={(e) => void handleSubmit((v) => save.mutate(v))(e)} className="flex flex-col gap-4">
      <FormField label="Name *" error={errors.name?.message}>
        <Input {...register('name')} autoFocus />
      </FormField>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="City" error={errors.city?.message}>
          <Input {...register('city')} />
        </FormField>
        <FormField label="Country" error={errors.country?.message}>
          <Input {...register('country')} />
        </FormField>
      </div>
      <FormField label="Notes" error={errors.notes?.message}>
        <textarea
          {...register('notes')}
          rows={3}
          className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-600"
        />
      </FormField>
      {save.isError && (
        <p className="text-sm text-red-400">{String(save.error)}</p>
      )}
      <div className="flex justify-end gap-2 pt-1">
        <Button type="button" onClick={onDone} className="bg-zinc-700 hover:bg-zinc-600">
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting || save.isPending}>
          {initial ? 'Save changes' : 'Create factory'}
        </Button>
      </div>
    </form>
  )
}

function FactoriesContent() {
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
  const [editing, setEditing] = useState<Factory | undefined>(undefined)
  const [confirmDelete, setConfirmDelete] = useState<Factory | undefined>(undefined)

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('new') === '1') {
      setEditing(undefined)
      setModalOpen(true)
      window.history.replaceState(null, '', '/factories')
    }
  }, [])

  const { data: factories = [], isLoading } = useQuery({
    queryKey: ['factories'],
    queryFn: () => getFactories(token),
    enabled: !!token,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteFactory(token, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['factories'] })
      setConfirmDelete(undefined)
    },
  })

  function openCreate() {
    setEditing(undefined)
    setModalOpen(true)
  }

  function openEdit(factory: Factory) {
    setEditing(factory)
    setModalOpen(true)
  }

  function closeModal() {
    setModalOpen(false)
    setEditing(undefined)
  }

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold">Factories</h1>
        {isAdmin && (
          <Button onClick={openCreate}>+ New factory</Button>
        )}
      </div>

      {isLoading ? (
        <p className="text-zinc-400">Loading…</p>
      ) : factories.length === 0 ? (
        <p className="text-zinc-500">No factories yet.{isAdmin ? ' Create one above.' : ''}</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-700">
          <table className="w-full text-sm">
            <thead className="bg-zinc-800 text-left text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">City</th>
                <th className="px-4 py-3 font-medium">Country</th>
                {isAdmin && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {factories.map((factory) => (
                <tr key={factory.id} className="hover:bg-zinc-800/50">
                  <td className="px-4 py-3 font-medium text-white">{factory.name}</td>
                  <td className="px-4 py-3 text-zinc-400">{factory.city ?? '—'}</td>
                  <td className="px-4 py-3 text-zinc-400">{factory.country ?? '—'}</td>
                  {isAdmin && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openEdit(factory)}
                        className="mr-3 text-zinc-400 hover:text-white"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmDelete(factory)}
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
        title={editing ? `Edit — ${editing.name}` : 'New factory'}
        onClose={closeModal}
      >
        <FactoryForm key={editing?.id ?? 'new'} initial={editing} token={token} onDone={closeModal} />
      </Modal>

      <Modal
        open={!!confirmDelete}
        title="Delete factory"
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

export default function FactoriesPage() {
  return (
    <RequireAuth>
      <AppLayout>
        <FactoriesContent />
      </AppLayout>
    </RequireAuth>
  )
}
