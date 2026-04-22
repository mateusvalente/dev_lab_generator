<template>
  <section>
    <div style="display:grid; gap:8px; max-width:420px;">
      <select v-model.number="form.CATEGORY_ID">
        <option :value="0">Selecione a categoria</option>
        <option v-for="item in categories" :key="item.ID" :value="item.ID">{{ item.NAME }}</option>
      </select>
      <input v-model="form.NAME" placeholder="Nome" />
      <input v-model.number="form.PRICE" type="number" step="0.01" placeholder="Preço" />
      <input v-model.number="form.STOCK" type="number" placeholder="Estoque" />
      <div style="display:flex; gap:8px;">
        <button @click="save">{{ form.ID ? 'Atualizar' : 'Adicionar' }}</button>
        <button v-if="form.ID" @click="reset">Cancelar</button>
      </div>
    </div>
    <table border="1" cellpadding="8" style="width:100%; margin-top:16px; border-collapse:collapse;">
      <thead><tr><th>ID</th><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ações</th></tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.ID">
          <td>{{ item.ID }}</td>
          <td>{{ item.NAME }}</td>
          <td>{{ item.CATEGORY_NAME || item.CATEGORY_ID }}</td>
          <td>{{ item.PRICE }}</td>
          <td>{{ item.STOCK }}</td>
          <td>
            <button @click="edit(item)">Editar</button>
            <button @click="remove(item.ID)">Excluir</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import { request } from '../api'

export default {
  data() {
    return {
      items: [],
      categories: [],
      form: { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 }
    }
  },
  async mounted() { await this.load() },
  methods: {
    async load() {
      this.categories = await request('/categories')
      this.items = await request('/products')
    },
    edit(item) { this.form = { ID: item.ID, CATEGORY_ID: Number(item.CATEGORY_ID), NAME: item.NAME, PRICE: Number(item.PRICE), STOCK: Number(item.STOCK) } },
    reset() { this.form = { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 } },
    async save() {
      if (this.form.ID) {
        await request(`/products/${this.form.ID}`, { method: 'PUT', body: JSON.stringify(this.form) })
      } else {
        await request('/products', { method: 'POST', body: JSON.stringify(this.form) })
      }
      this.reset()
      await this.load()
    },
    async remove(id) {
      await request(`/products/${id}`, { method: 'DELETE' })
      await this.load()
    }
  }
}
</script>
