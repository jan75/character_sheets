<template>          
  <td>{{ entry.name }} ({{ entry.id }})</td>
  <td>{{ entry.year }}</td>
  <td>{{ entry.series.name }}</td>
  <td>{{ entry.entrytype.type }}</td>
  <td><button type="button" v-on:click="onEdit()">Edit</button> <button type="button" v-on:click="onDelete()">Delete</button></td>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { Entry } from '../../../assets/ts/entries'

const EntryRow = defineComponent({
  props: {
    entry: Object as PropType<Entry>
  },
  methods: {
    onEdit() {
      console.log('edit clicked', this);
      //this.$emit('entryEdited');
    },
    onDelete() {
      console.log('delete clicked', this);
    }
  }
})

export default EntryRow;
</script>