import Head from 'next/head'
import { useEffect, useState } from 'react'
import { request } from '../lib/api'

const emptyForm = { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 }

export default function Products() {
  const [items, setItems] = useState([])
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [message, setMessage] = useState('')

  const load = async () => {
    try {
      setCategories(await request('/categories'))
      setItems(await request('/products'))
      setMessage('Produtos carregados com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao carregar produtos.')
    }
  }

  useEffect(() => { load() }, [])

  const save = async () => {
    try {
      if (form.ID) await request(`/products/${form.ID}`, { method: 'PUT', body: JSON.stringify(form) })
      else await request('/products', { method: 'POST', body: JSON.stringify(form) })
      setForm(emptyForm)
      await load()
      setMessage('Produto salvo com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao salvar produto.')
    }
  }

  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <meta httpEquiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Next MPA - Produtos</title>
      </Head>
      <main style={{ fontFamily: 'Arial', padding: 24, maxWidth: 1100, margin: '0 auto' }}>
        <nav><a href="/">Início</a> | <a href="/categories">Categorias</a></nav>
        <h1>Produtos</h1>
        {message ? <div style={{ margin: '16px 0', padding: 12, background: '#eef6ff', border: '1px solid #c9def8', borderRadius: 8 }}>{message}</div> : null}
        <div style={{ display: 'grid', gap: 8, maxWidth: 420 }}>
          <select value={form.CATEGORY_ID} onChange={e => setForm({ ...form, CATEGORY_ID: Number(e.target.value) })}>
            <option value={0}>Selecione a categoria</option>
            {categories.map(item => <option key={item.ID} value={item.ID}>{item.NAME}</option>)}
          </select>
          <input placeholder="Nome" value={form.NAME} onChange={e => setForm({ ...form, NAME: e.target.value })} />
          <input type="number" step="0.01" placeholder="Preço" value={form.PRICE} onChange={e => setForm({ ...form, PRICE: Number(e.target.value) })} />
          <input type="number" placeholder="Estoque" value={form.STOCK} onChange={e => setForm({ ...form, STOCK: Number(e.target.value) })} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={save}>{form.ID ? 'Atualizar' : 'Adicionar'}</button>
            {form.ID ? <button onClick={() => setForm(emptyForm)}>Cancelar</button> : null}
          </div>
        </div>
        <table border="1" cellPadding="8" style={{ width: '100%', marginTop: 16, borderCollapse: 'collapse' }}>
          <thead><tr><th>ID</th><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ações</th></tr></thead>
          <tbody>{items.map(item => <tr key={item.ID}><td>{item.ID}</td><td>{item.NAME}</td><td>{item.CATEGORY_NAME || item.CATEGORY_ID}</td><td>{item.PRICE}</td><td>{item.STOCK}</td><td><button onClick={() => setForm({ ID: item.ID, CATEGORY_ID: Number(item.CATEGORY_ID), NAME: item.NAME, PRICE: Number(item.PRICE), STOCK: Number(item.STOCK) })}>Editar</button> <button onClick={async () => { await request(`/products/${item.ID}`, { method: 'DELETE' }); await load(); setMessage('Produto removido com sucesso.') }}>Excluir</button></td></tr>)}</tbody>
        </table>
      </main>
    </>
  )
}
