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
import { getBrands, createBrand, updateBrand, deleteBrand, type Brand } from '../api/brands'

const schema = z.object({
  name: z.string().min(1, 'Required'),
  country: z.string().optional(),
  website: z.string().optional(),
  notes: z.string().optional(),
})
type FormData = z.infer<typeof schema>

function BrandForm({
  initial,
  token,
  onDone,
}: {
  initial?: Brand
  token: string
  onDone: () => void
}) {
  const queryClient = useQueryClient()

  const save = useMutation({
    mutationFn: (data: FormData) =>
      initial ? updateBrand(token, initial.id, data) : createBrand(token, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['brands'] })
      onDone()
    },
  })

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? '',
      country: initial?.country ?? '',
      website: initial?.website ?? '',
      notes: initial?.notes ?? '',
    },
  })

  return (
    <form onSubmit={(e) => void handleSubmit((v) => save.mutate(v))(e)} className="flex flex-col gap-4">
      <FormField label="Name *" error={errors.name?.message}>
        <Input {...register('name')} autoFocus />
      </FormField>
      <FormField label="Country" error={errors.country?.message}>
        <Input {...register('country')} />
      </FormField>
      <FormField label="Website" error={errors.website?.message}>
        <Input {...register('website')} placeholder="https://" />
      </FormField>
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
          {initial ? 'Save changes' : 'Create brand'}
        </Button>
      </div>
    </form>
  )
}

function BrandsContent() {
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
  const [editing, setEditing] = useState<Brand | undefined>(undefined)
  const [confirmDelete, setConfirmDelete] = useState<Brand | undefined>(undefined)

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('new') === '1') {
      setEditing(undefined)
      setModalOpen(true)
      window.history.replaceState(null, '', '/brands')
    }
  }, [])

  const { data: brands = [], isLoading } = useQuery({
    queryKey: ['brands'],
    queryFn: () => getBrands(token),
    enabled: !!token,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteBrand(token, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['brands'] })
      setConfirmDelete(undefined)
    },
  })

  function openCreate() {
    setEditing(undefined)
    setModalOpen(true)
  }

  function openEdit(brand: Brand) {
    setEditing(brand)
    setModalOpen(true)
  }

  function closeModal() {
    setModalOpen(false)
    setEditing(undefined)
  }

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold">Brands</h1>
        {isAdmin && (
          <Button onClick={openCreate}>+ New brand</Button>
        )}
      </div>

      {isLoading ? (
        <p className="text-zinc-400">Loading…</p>
      ) : brands.length === 0 ? (
        <p className="text-zinc-500">No brands yet.{isAdmin ? ' Create one above.' : ''}</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-700">
          <table className="w-full text-sm">
            <thead className="bg-zinc-800 text-left text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Country</th>
                <th className="px-4 py-3 font-medium">Website</th>
                {isAdmin && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {brands.map((brand) => (
                <tr key={brand.id} className="hover:bg-zinc-800/50">
                  <td className="px-4 py-3 font-medium text-white">{brand.name}</td>
                  <td className="px-4 py-3 text-zinc-400">{brand.country ?? '—'}</td>
                  <td className="px-4 py-3 text-zinc-400">
                    {brand.website ? (
                      <a
                        href={brand.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-amber-500 hover:underline"
                      >
                        {brand.website.replace(/^https?:\/\//, '')}
                      </a>
                    ) : '—'}
                  </td>
                  {isAdmin && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openEdit(brand)}
                        className="mr-3 text-zinc-400 hover:text-white"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmDelete(brand)}
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
        title={editing ? `Edit — ${editing.name}` : 'New brand'}
        onClose={closeModal}
      >
        <BrandForm key={editing?.id ?? 'new'} initial={editing} token={token} onDone={closeModal} />
      </Modal>

      <Modal
        open={!!confirmDelete}
        title="Delete brand"
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

export default function BrandsPage() {
  return (
    <RequireAuth>
      <AppLayout>
        <BrandsContent />
      </AppLayout>
    </RequireAuth>
  )
}
