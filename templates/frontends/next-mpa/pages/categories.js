import Head from 'next/head'
import { useEffect, useState } from 'react'
import { request } from '../lib/api'

const emptyForm = { ID: null, NAME: '', DESCRIPTION: '' }

export default function Categories() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [message, setMessage] = useState('')

  const load = async () => {
    try {
      setItems(await request('/categories'))
      setMessage('Categorias carregadas com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao carregar categorias.')
    }
  }

  useEffect(() => { load() }, [])

  const save = async () => {
    try {
      if (form.ID) await request(`/categories/${form.ID}`, { method: 'PUT', body: JSON.stringify(form) })
      else await request('/categories', { method: 'POST', body: JSON.stringify(form) })
      setForm(emptyForm)
      await load()
      setMessage('Categoria salva com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao salvar categoria.')
    }
  }

  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <meta httpEquiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Next MPA - Categorias</title>
      </Head>
      <main style={{ fontFamily: 'Arial', padding: 24, maxWidth: 1000, margin: '0 auto' }}>
        <nav><a href="/">Início</a> | <a href="/products">Produtos</a></nav>
        <h1>Categorias</h1>
        {message ? <div style={{ margin: '16px 0', padding: 12, background: '#eef6ff', border: '1px solid #c9def8', borderRadius: 8 }}>{message}</div> : null}
        <div style={{ display: 'grid', gap: 8, maxWidth: 420 }}>
          <input placeholder="Nome" value={form.NAME} onChange={e => setForm({ ...form, NAME: e.target.value })} />
          <input placeholder="Descrição" value={form.DESCRIPTION} onChange={e => setForm({ ...form, DESCRIPTION: e.target.value })} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={save}>{form.ID ? 'Atualizar' : 'Adicionar'}</button>
            {form.ID ? <button onClick={() => setForm(emptyForm)}>Cancelar</button> : null}
          </div>
        </div>
        <table border="1" cellPadding="8" style={{ width: '100%', marginTop: 16, borderCollapse: 'collapse' }}>
          <thead><tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
          <tbody>{items.map(item => <tr key={item.ID}><td>{item.ID}</td><td>{item.NAME}</td><td>{item.DESCRIPTION}</td><td><button onClick={() => setForm({ ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' })}>Editar</button> <button onClick={async () => { await request(`/categories/${item.ID}`, { method: 'DELETE' }); await load(); setMessage('Categoria removida com sucesso.') }}>Excluir</button></td></tr>)}</tbody>
        </table>
      </main>
    </>
  )
}
