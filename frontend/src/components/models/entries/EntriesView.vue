<template>
  <div class="entries-view">
    <p>Entries view:</p>
    <EntriesTable v-bind:refresh="refresh" />
    <EntriesForm v-on:entry-added="refreshEntries" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import EntriesForm from './EntriesForm.vue'
import EntriesTable from './EntriesTable.vue'

const EntriesView = defineComponent({
  components: {
    EntriesForm,
    EntriesTable
  },
  data() {
    return {
      refresh: 0
    }
  },
  methods: {
    refreshEntries() {
      console.log('refreshEntries() called');
      this.refresh = this.refresh + 1;
    }
  }
})

export default EntriesView;
</script>