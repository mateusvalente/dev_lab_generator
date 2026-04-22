<template>
  <main style="font-family: Arial, sans-serif; padding: 24px; max-width: 1200px; margin: 0 auto;">
    <h1>Laboratório CRUD - Vue SPA</h1>
    <p>Uma única página controlando categorias e produtos.</p>
    <div v-if="message" style="margin-bottom:16px; padding:12px; background:#eef6ff; border:1px solid #c9def8; border-radius:8px;">{{ message }}</div>
    <div class="grid" style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
      <section style="border:1px solid #ddd; border-radius:12px; padding:16px;">
        <h2>Categorias</h2>
        <div style="display:grid; gap:8px;">
          <input v-model="category.NAME" placeholder="Nome" />
          <input v-model="category.DESCRIPTION" placeholder="Descrição" />
          <div style="display:flex; gap:8px;">
            <button @click="saveCategory">{{ category.ID ? 'Atualizar' : 'Adicionar' }}</button>
            <button v-if="category.ID" @click="resetCategory">Cancelar</button>
          </div>
        </div>
        <table border="1" cellpadding="8" style="width:100%; margin-top:12px; border-collapse:collapse;">
          <thead><tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
          <tbody>
            <tr v-for="item in categories" :key="item.ID">
              <td>{{ item.ID }}</td>
              <td>{{ item.NAME }}</td>
              <td>{{ item.DESCRIPTION }}</td>
              <td>
                <button @click="editCategory(item)">Editar</button>
                <button @click="removeCategory(item.ID)">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section style="border:1px solid #ddd; border-radius:12px; padding:16px;">
        <h2>Produtos</h2>
        <div style="display:grid; gap:8px;">
          <select v-model.number="product.CATEGORY_ID">
            <option :value="0">Selecione a categoria</option>
            <option v-for="item in categories" :key="item.ID" :value="item.ID">{{ item.NAME }}</option>
          </select>
          <input v-model="product.NAME" placeholder="Nome" />
          <input v-model.number="product.PRICE" type="number" step="0.01" placeholder="Preço" />
          <input v-model.number="product.STOCK" type="number" placeholder="Estoque" />
          <div style="display:flex; gap:8px;">
            <button @click="saveProduct">{{ product.ID ? 'Atualizar' : 'Adicionar' }}</button>
            <button v-if="product.ID" @click="resetProduct">Cancelar</button>
          </div>
        </div>
        <table border="1" cellpadding="8" style="width:100%; margin-top:12px; border-collapse:collapse;">
          <thead><tr><th>ID</th><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ações</th></tr></thead>
          <tbody>
            <tr v-for="item in products" :key="item.ID">
              <td>{{ item.ID }}</td>
              <td>{{ item.NAME }}</td>
              <td>{{ item.CATEGORY_NAME || item.CATEGORY_ID }}</td>
              <td>{{ item.PRICE }}</td>
              <td>{{ item.STOCK }}</td>
              <td>
                <button @click="editProduct(item)">Editar</button>
                <button @click="removeProduct(item.ID)">Excluir</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { request } from './api'

const categories = ref([])
const products = ref([])
const message = ref('')
const category = reactive({ ID: null, NAME: '', DESCRIPTION: '' })
const product = reactive({ ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 })

const load = async () => {
  try {
    categories.value = await request('/categories')
    products.value = await request('/products')
    message.value = 'Dados carregados com sucesso.'
  } catch (error) {
    message.value = error.message || 'Falha ao carregar dados.'
  }
}

const resetCategory = () => Object.assign(category, { ID: null, NAME: '', DESCRIPTION: '' })
const resetProduct = () => Object.assign(product, { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 })

const saveCategory = async () => {
  try {
    if (category.ID) {
      await request(`/categories/${category.ID}`, { method: 'PUT', body: JSON.stringify(category) })
    } else {
      await request('/categories', { method: 'POST', body: JSON.stringify(category) })
    }
    resetCategory()
    await load()
    message.value = 'Categoria salva com sucesso.'
  } catch (error) {
    message.value = error.message || 'Falha ao salvar categoria.'
  }
}

const saveProduct = async () => {
  try {
    if (product.ID) {
      await request(`/products/${product.ID}`, { method: 'PUT', body: JSON.stringify(product) })
    } else {
      await request('/products', { method: 'POST', body: JSON.stringify(product) })
    }
    resetProduct()
    await load()
    message.value = 'Produto salvo com sucesso.'
  } catch (error) {
    message.value = error.message || 'Falha ao salvar produto.'
  }
}

const editCategory = (item) => Object.assign(category, { ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' })
const editProduct = (item) => Object.assign(product, { ID: item.ID, CATEGORY_ID: Number(item.CATEGORY_ID), NAME: item.NAME, PRICE: Number(item.PRICE), STOCK: Number(item.STOCK) })
const removeCategory = async (id) => { try { await request(`/categories/${id}`, { method: 'DELETE' }); await load(); message.value = 'Categoria removida com sucesso.' } catch (error) { message.value = error.message || 'Falha ao remover categoria.' } }
const removeProduct = async (id) => { try { await request(`/products/${id}`, { method: 'DELETE' }); await load(); message.value = 'Produto removido com sucesso.' } catch (error) { message.value = error.message || 'Falha ao remover produto.' } }

onMounted(load)
</script>
