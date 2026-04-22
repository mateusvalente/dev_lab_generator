<template>
  <section>
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
  </section>
</template>

<script>
import { request } from '../api'

export default {
  data() {
    return {
      items: [],
      form: { ID: null, NAME: '', DESCRIPTION: '' }
    }
  },
  async mounted() { await this.load() },
  methods: {
    async load() { this.items = await request('/categories') },
    edit(item) { this.form = { ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' } },
    reset() { this.form = { ID: null, NAME: '', DESCRIPTION: '' } },
    async save() {
      if (this.form.ID) {
        await request(`/categories/${this.form.ID}`, { method: 'PUT', body: JSON.stringify(this.form) })
      } else {
        await request('/categories', { method: 'POST', body: JSON.stringify(this.form) })
      }
      this.reset()
      await this.load()
    },
    async remove(id) {
      await request(`/categories/${id}`, { method: 'DELETE' })
      await this.load()
    }
  }
}
</script>
