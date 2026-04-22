import { createApp } from 'vue'
import { request } from './api'

createApp({
  data: () => ({
    items: [],
    message: '',
    form: { ID: null, NAME: '', DESCRIPTION: '' }
  }),
  async mounted() { await this.load() },
  methods: {
    async load() {
      try {
        this.items = await request('/categories')
        this.message = 'Categorias carregadas com sucesso.'
      } catch (error) {
        this.message = error.message || 'Falha ao carregar categorias.'
      }
    },
    edit(item) { this.form = { ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' } },
    reset() { this.form = { ID: null, NAME: '', DESCRIPTION: '' } },
    async save() {
      try {
        if (this.form.ID) {
          await request(`/categories/${this.form.ID}`, { method: 'PUT', body: JSON.stringify(this.form) })
        } else {
          await request('/categories', { method: 'POST', body: JSON.stringify(this.form) })
        }
        this.reset()
        await this.load()
        this.message = 'Categoria salva com sucesso.'
      } catch (error) {
        this.message = error.message || 'Falha ao salvar categoria.'
      }
    },
    async remove(id) {
      try {
        await request(`/categories/${id}`, { method: 'DELETE' })
        await this.load()
        this.message = 'Categoria removida com sucesso.'
      } catch (error) {
        this.message = error.message || 'Falha ao remover categoria.'
      }
    }
  },
  template: `
    <main style="font-family: Arial, sans-serif; padding: 24px; max-width: 1000px; margin: 0 auto;">
      <nav><a href="/index.html">Início</a> | <a href="/products.html">Produtos</a></nav>
      <h1>Categorias</h1>
      <div v-if="message" style="margin:16px 0; padding:12px; background:#eef6ff; border:1px solid #c9def8; border-radius:8px;">{{ message }}</div>
      <div style="display:grid; gap:8px; max-width:420px;">
        <input v-model="form.NAME" placeholder="Nome" />
        <input v-model="form.DESCRIPTION" placeholder="Descrição" />
        <div style="display:flex; gap:8px;">
          <button @click="save">{{ form.ID ? 'Atualizar' : 'Adicionar' }}</button>
          <button v-if="form.ID" @click="reset">Cancelar</button>
        </div>
      </div>
      <table border="1" cellpadding="8" style="width:100%; margin-top:16px; border-collapse:collapse;">
        <thead><tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
        <tbody>
          <tr v-for="item in items" :key="item.ID">
            <td>{{ item.ID }}</td>
            <td>{{ item.NAME }}</td>
            <td>{{ item.DESCRIPTION }}</td>
            <td>
              <button @click="edit(item)">Editar</button>
              <button @click="remove(item.ID)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </main>
  `
}).mount('#app')
