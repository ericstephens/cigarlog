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
import { getCigars, createCigar, updateCigar, deleteCigar, type Cigar } from '../api/cigars'
import { getBrands } from '../api/brands'
import { getFactories } from '../api/factories'
import { getVitolas } from '../api/vitolas'

const STRENGTHS = ['mild', 'mild-medium', 'medium', 'medium-full', 'full']

const schema = z.object({
  name: z.string().min(1, 'Required'),
  brand_id: z.string().min(1, 'Required'),
  factory_id: z.string().optional(),
  vitola_id: z.string().optional(),
  wrapper: z.string().optional(),
  binder_origin: z.string().optional(),
  filler_origin: z.string().optional(),
  strength: z.string().optional(),
  msrp: z.string().optional(),
  description: z.string().optional(),
})
type FormData = z.infer<typeof schema>

function CigarForm({
  initial,
  token,
  onDone,
}: {
  initial?: Cigar
  token: string
  onDone: () => void
}) {
  const queryClient = useQueryClient()

  const { data: brands = [] } = useQuery({
    queryKey: ['brands'],
    queryFn: () => getBrands(token),
    enabled: !!token,
  })

  const { data: factories = [] } = useQuery({
    queryKey: ['factories'],
    queryFn: () => getFactories(token),
    enabled: !!token,
  })

  const { data: vitolas = [] } = useQuery({
    queryKey: ['vitolas'],
    queryFn: () => getVitolas(token),
    enabled: !!token,
  })

  const save = useMutation({
    mutationFn: (data: FormData) =>
      initial ? updateCigar(token, initial.id, data) : createCigar(token, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['cigars'] })
      onDone()
    },
  })

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? '',
      brand_id: initial?.brand_id ?? '',
      factory_id: initial?.factory_id ?? '',
      vitola_id: initial?.vitola_id ?? '',
      wrapper: initial?.wrapper ?? '',
      binder_origin: initial?.binder_origin ?? '',
      filler_origin: initial?.filler_origin ?? '',
      strength: initial?.strength ?? '',
      msrp: initial?.msrp ?? '',
      description: initial?.description ?? '',
    },
  })

  return (
    <form onSubmit={(e) => void handleSubmit((v) => save.mutate(v))(e)} className="flex flex-col gap-4">
      <FormField label="Name *" error={errors.name?.message}>
        <Input {...register('name')} autoFocus />
      </FormField>
      <FormField label="Brand *" error={errors.brand_id?.message}>
        <select
          {...register('brand_id')}
          className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-600"
        >
          <option value="">— Select brand —</option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>
      </FormField>
      <FormField label="Factory" error={errors.factory_id?.message}>
        <select
          {...register('factory_id')}
          className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-600"
        >
          <option value="">— None —</option>
          {factories.map((f) => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      </FormField>
      <FormField label="Vitola" error={errors.vitola_id?.message}>
        <select
          {...register('vitola_id')}
          className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-600"
        >
          <option value="">— None —</option>
          {vitolas.map((v) => (
            <option key={v.id} value={v.id}>{v.name}</option>
          ))}
        </select>
      </FormField>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Wrapper" error={errors.wrapper?.message}>
          <Input {...register('wrapper')} placeholder="e.g. Connecticut" />
        </FormField>
        <FormField label="Strength" error={errors.strength?.message}>
          <select
            {...register('strength')}
            className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-600"
          >
            <option value="">— Select —</option>
            {STRENGTHS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </FormField>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Binder Origin" error={errors.binder_origin?.message}>
          <Input {...register('binder_origin')} />
        </FormField>
        <FormField label="Filler Origin" error={errors.filler_origin?.message}>
          <Input {...register('filler_origin')} />
        </FormField>
      </div>
      <FormField label="MSRP ($)" error={errors.msrp?.message}>
        <Input {...register('msrp')} placeholder="e.g. 24.99" />
      </FormField>
      <FormField label="Description" error={errors.description?.message}>
        <textarea
          {...register('description')}
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
          {initial ? 'Save changes' : 'Create cigar'}
        </Button>
      </div>
    </form>
  )
}

function CigarsContent() {
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
  const [editing, setEditing] = useState<Cigar | undefined>(undefined)
  const [confirmDelete, setConfirmDelete] = useState<Cigar | undefined>(undefined)

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('new') === '1') {
      setEditing(undefined)
      setModalOpen(true)
      window.history.replaceState(null, '', '/cigars')
    }
  }, [])

  const { data: cigars = [], isLoading } = useQuery({
    queryKey: ['cigars'],
    queryFn: () => getCigars(token),
    enabled: !!token,
  })

  const { data: brands = [] } = useQuery({
    queryKey: ['brands'],
    queryFn: () => getBrands(token),
    enabled: !!token,
  })

  const remove = useMutation({
    mutationFn: (id: string) => deleteCigar(token, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['cigars'] })
      setConfirmDelete(undefined)
    },
  })

  function openCreate() {
    setEditing(undefined)
    setModalOpen(true)
  }

  function openEdit(cigar: Cigar) {
    setEditing(cigar)
    setModalOpen(true)
  }

  function closeModal() {
    setModalOpen(false)
    setEditing(undefined)
  }

  const brandMap = Object.fromEntries(brands.map((b) => [b.id, b.name]))

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold">Cigars</h1>
        {isAdmin && (
          <Button onClick={openCreate}>+ New cigar</Button>
        )}
      </div>

      {isLoading ? (
        <p className="text-zinc-400">Loading…</p>
      ) : cigars.length === 0 ? (
        <p className="text-zinc-500">No cigars yet.{isAdmin ? ' Create one above.' : ''}</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-700">
          <table className="w-full text-sm">
            <thead className="bg-zinc-800 text-left text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Brand</th>
                <th className="px-4 py-3 font-medium">Strength</th>
                <th className="px-4 py-3 font-medium">MSRP</th>
                {isAdmin && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {cigars.map((cigar) => (
                <tr key={cigar.id} className="hover:bg-zinc-800/50">
                  <td className="px-4 py-3 font-medium text-white">{cigar.name}</td>
                  <td className="px-4 py-3 text-zinc-400">{brandMap[cigar.brand_id] ?? cigar.brand_id}</td>
                  <td className="px-4 py-3 text-zinc-400">{cigar.strength ?? '—'}</td>
                  <td className="px-4 py-3 text-zinc-400">{cigar.msrp ? `$${cigar.msrp}` : '—'}</td>
                  {isAdmin && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openEdit(cigar)}
                        className="mr-3 text-zinc-400 hover:text-white"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmDelete(cigar)}
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
        title={editing ? `Edit — ${editing.name}` : 'New cigar'}
        onClose={closeModal}
      >
        <CigarForm key={editing?.id ?? 'new'} initial={editing} token={token} onDone={closeModal} />
      </Modal>

      <Modal
        open={!!confirmDelete}
        title="Delete cigar"
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

export default function CigarsPage() {
  return (
    <RequireAuth>
      <AppLayout>
        <CigarsContent />
      </AppLayout>
    </RequireAuth>
  )
}
