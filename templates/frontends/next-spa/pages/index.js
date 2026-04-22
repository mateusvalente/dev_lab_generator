import Head from 'next/head'
import { useEffect, useState } from 'react'
import { request } from '../lib/api'

const emptyCategory = { ID: null, NAME: '', DESCRIPTION: '' }
const emptyProduct = { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 }

export default function Home() {
  const [categories, setCategories] = useState([])
  const [products, setProducts] = useState([])
  const [category, setCategory] = useState(emptyCategory)
  const [product, setProduct] = useState(emptyProduct)
  const [message, setMessage] = useState('')

  const load = async () => {
    try {
      setCategories(await request('/categories'))
      setProducts(await request('/products'))
      setMessage('Dados carregados com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao carregar dados.')
    }
  }

  useEffect(() => { load() }, [])

  const saveCategory = async () => {
    try {
      if (category.ID) {
        await request(`/categories/${category.ID}`, { method: 'PUT', body: JSON.stringify(category) })
      } else {
        await request('/categories', { method: 'POST', body: JSON.stringify(category) })
      }
      setCategory(emptyCategory)
      await load()
      setMessage('Categoria salva com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao salvar categoria.')
    }
  }

  const saveProduct = async () => {
    try {
      if (product.ID) {
        await request(`/products/${product.ID}`, { method: 'PUT', body: JSON.stringify(product) })
      } else {
        await request('/products', { method: 'POST', body: JSON.stringify(product) })
      }
      setProduct(emptyProduct)
      await load()
      setMessage('Produto salvo com sucesso.')
    } catch (error) {
      setMessage(error.message || 'Falha ao salvar produto.')
    }
  }

  const removeCategory = async (id) => {
    await request(`/categories/${id}`, { method: 'DELETE' })
    await load()
    setMessage('Categoria removida com sucesso.')
  }

  const removeProduct = async (id) => {
    await request(`/products/${id}`, { method: 'DELETE' })
    await load()
    setMessage('Produto removido com sucesso.')
  }

  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <meta httpEquiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Next SPA CRUD</title>
      </Head>
      <main style={{ fontFamily: 'Arial', padding: 24, maxWidth: 1200, margin: '0 auto' }}>
        <h1>Laboratório CRUD - Next SPA</h1>
        <p>Uma única página controlando categorias e produtos.</p>
        {message ? <div style={{ marginBottom: 16, padding: 12, background: '#eef6ff', border: '1px solid #c9def8', borderRadius: 8 }}>{message}</div> : null}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <section style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
            <h2>Categorias</h2>
            <div style={{ display: 'grid', gap: 8 }}>
              <input placeholder="Nome" value={category.NAME} onChange={e => setCategory({ ...category, NAME: e.target.value })} />
              <input placeholder="Descrição" value={category.DESCRIPTION} onChange={e => setCategory({ ...category, DESCRIPTION: e.target.value })} />
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={saveCategory}>{category.ID ? 'Atualizar' : 'Adicionar'}</button>
                {category.ID ? <button onClick={() => setCategory(emptyCategory)}>Cancelar</button> : null}
              </div>
            </div>
            <table border="1" cellPadding="8" style={{ width: '100%', marginTop: 12, borderCollapse: 'collapse' }}>
              <thead><tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
              <tbody>{categories.map(item => <tr key={item.ID}><td>{item.ID}</td><td>{item.NAME}</td><td>{item.DESCRIPTION}</td><td><button onClick={() => setCategory({ ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' })}>Editar</button> <button onClick={() => removeCategory(item.ID)}>Excluir</button></td></tr>)}</tbody>
            </table>
          </section>
          <section style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
            <h2>Produtos</h2>
            <div style={{ display: 'grid', gap: 8 }}>
              <select value={product.CATEGORY_ID} onChange={e => setProduct({ ...product, CATEGORY_ID: Number(e.target.value) })}>
                <option value={0}>Selecione a categoria</option>
                {categories.map(item => <option key={item.ID} value={item.ID}>{item.NAME}</option>)}
              </select>
              <input placeholder="Nome" value={product.NAME} onChange={e => setProduct({ ...product, NAME: e.target.value })} />
              <input type="number" step="0.01" placeholder="Preço" value={product.PRICE} onChange={e => setProduct({ ...product, PRICE: Number(e.target.value) })} />
              <input type="number" placeholder="Estoque" value={product.STOCK} onChange={e => setProduct({ ...product, STOCK: Number(e.target.value) })} />
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={saveProduct}>{product.ID ? 'Atualizar' : 'Adicionar'}</button>
                {product.ID ? <button onClick={() => setProduct(emptyProduct)}>Cancelar</button> : null}
              </div>
            </div>
            <table border="1" cellPadding="8" style={{ width: '100%', marginTop: 12, borderCollapse: 'collapse' }}>
              <thead><tr><th>ID</th><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ações</th></tr></thead>
              <tbody>{products.map(item => <tr key={item.ID}><td>{item.ID}</td><td>{item.NAME}</td><td>{item.CATEGORY_NAME || item.CATEGORY_ID}</td><td>{item.PRICE}</td><td>{item.STOCK}</td><td><button onClick={() => setProduct({ ID: item.ID, CATEGORY_ID: Number(item.CATEGORY_ID), NAME: item.NAME, PRICE: Number(item.PRICE), STOCK: Number(item.STOCK) })}>Editar</button> <button onClick={() => removeProduct(item.ID)}>Excluir</button></td></tr>)}</tbody>
            </table>
          </section>
        </div>
      </main>
    </>
  )
}
