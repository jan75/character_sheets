<template>
  <form class="entries-form" v-on:submit="addEntry">
    <div class="entries-form-inputgroup">
      <label for="entries-form-input-name">Name:</label>
      <input type="text" name="name" id="entries-form-input-name" required>
    </div>
    <div class="entries-form-inputgroup">
      <label for="entries-form-input-year">Year:</label>
      <input type="date" name="date" id="entries-form-input-year">
    </div>
    <!--
    <div class="entries-form-inputgroup">
      <label for="entries-form-input-series">Series:</label>
      <Vue-select v-bind:options="seriesOptions" v-model="seriesSelected" v-on:search="searchSeries" label="name" name="series" />
    </div>
    -->
    <div class="entries-form-inputgroup">
      <button type="submit">Submit</button>
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { createApiRequest } from '../../../assets/ts/network'
//import vSelect from 'vue-select';
//import 'vue-select/dist/vue-select.css';

const EntriesForm = defineComponent({  
  /*components: {
    'Vue-select': vSelect
  },*/
  data() {
    return {
      seriesSelected: null,
      seriesOptions: []
    }
  },
  methods: {
    addEntry(submitEvent: any) {
      submitEvent.preventDefault();

      // form validation
      try {
        var name = submitEvent.target.elements.name.value;
        if (!name) {
          throw "Name can't be empty";
        }

        var date = new Date(submitEvent.target.elements.date.value);
        if (isNaN(date.getFullYear())) {
          throw "Invalid date";
        }

        /*
        if (isNaN(this.seriesSelected.id)) {
          throw "Series ID is null or not a number"
        }
        */
      } catch (error) {
        console.error(error);
        return;
      }

      console.log('submitEvent:', submitEvent);
      var data = {
        name: name,
        year: date.getFullYear(),
        seriesId: 1,
        entrytypeId: 1
      }

      var requestOptions = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      }

      createApiRequest('http://localhost:5000/rest/entries', requestOptions)
        .then(() => {
          console.log('Entry created');
          this.$emit('entry-added');
        })
        .catch((message) => {
          console.error('Could not create entry', message);
        });
      
    }
    /*
    searchSeries(name) {
      if (name) {
        fetchJsonDataRequest('http://localhost:5000/rest/series/search?offset=0&q=' + name)
          .then((data) => {
            console.log('Series searched');
            this.seriesOptions = data['data']
          })
          .catch((message) => {
            console.error('Could not search series', message);
          });
      }
    }
    */
  }
})

export default EntriesForm;
</script>