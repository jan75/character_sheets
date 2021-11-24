<template>
  <div class="entries-table">
    <button v-if="totalPages" v-on:click="prevPage" type="button">prev</button> <button v-if="totalPages" v-on:click="nextPage" type="button">next</button>
    <table v-if="entries">
      <thead>
        <tr>
          <th>Name</th>
          <th>Year</th>
          <th>Series</th>
          <th>Type</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in entries" v-bind:key="entry.id">
          <EntryRow v-bind:entry="entry" 
                    v-on:entry-edited="fetchData()" />
        </tr>
      </tbody>
    </table>
    <p v-if="totalPages">Page {{ page }} / {{ totalPages }} ({{ size }} entries, {{ limit }} per page)</p>
    <button v-if="totalPages" v-on:click="prevPage" type="button">prev</button> <button v-if="totalPages" v-on:click="nextPage" type="button">next</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { fetchJsonDataRequest } from '../../../assets/ts/network'
import EntryRow from './EntryRow.vue'


const EntriesTable = defineComponent({
  components: {
    EntryRow
  },
  props: {
    seriesId: Number,
    refresh: Number
  },
  data() {
    return {      
      entries: [],
      size: 0,
      offset: 0,
      limit: 0,
      page: 1
    }
  },
  computed: {
    totalPages(): Number {
      if (isNaN(this.size) || isNaN(this.limit)) {
        return 0;
      } else {
        return Math.ceil(this.size / this.limit)
      }
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData(): void {
        fetchJsonDataRequest('http://localhost:5000/rest/entries?offset=' + this.offset)
          .then((data) => {
            console.log('Data fetched');
            this.entries = data['data'];
            this.size = data['size'];
            this.offset = data['offset'];
            this.limit = data['limit'];
          })
          .catch((message) => {
            console.error('Could not fetch entries', message);
          });
    },
    prevPage(): void {
      console.log('prevPage()');
      if(this.offset - this.limit >= 0 && this.page >= 2) {
        this.offset = this.offset - this.limit;
        this.fetchData();
        this.page = this.page - 1;
      }
    },
    nextPage(): void {
      console.log('nextPage()');
      if(this.size > (this.offset + this.limit)) {
        this.offset = this.offset + this.limit;
        this.fetchData();
        this.page = this.page + 1;
      }
    }
  },
  watch: {
    refresh(newValue, oldValue) {
      console.log('watch triggered on refresh', oldValue, newValue);
      if(newValue > oldValue && newValue > 0) {
        this.fetchData();
      }
    }
  }
})

export default EntriesTable;
</script>