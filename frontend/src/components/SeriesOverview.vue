<template>

  <div class="columns">

    <div class="column is-two-thirds">
      <form class="field has-addons" v-on:submit="search">
        <div class="control is-expanded">
          <input class="input" type="text" name="search" />
        </div>
        <div class="control">
          <button class="button is-primary" type="submit" v-on:submit="search">Search</button>
        </div>
      </form>
    </div>
  </div>

  <div class="columns">
    <div class="column is-two-thirds">

      <div v-if="series">
        <table v-if="series" class="table is-hoverable is-fullwidth">
          <thead>
            <tr>
              <th>Series</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in series" v-bind:key="s.id" >
              <td>
                <router-link class="series-table-link" v-bind:to="'/series/' + s.id">
                  <div class="block">{{ s.name }}</div>
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>

        <nav v-if="totalPages" class="pagination" role="navigation" aria-label="navigation">
          <div class="buttons has-addons">
            <button class="button level-item" type="button" v-on:click="prevPage">&lt;</button>
            <button class="button level-item" type="button" v-on:click="nextPage">&gt;</button>          
          </div>
          <p>Page {{ page }} / {{ totalPages }} ({{ size }} total, {{ limit }} per page)</p>
        </nav>
      </div>
    
    </div>
    <div class="column">
      
      <form v-on:submit="addSeries">
        <div class="field is-horizontal">
          <div class="field-label is-normal">
            <label class="label">Name</label>
          </div>
          <div class="field-body">
            <div class="field">
              <div class="control is-expanded">
                <input v-bind:class="{ 'is-danger': inputNameMessage }" class="input" type="text" name="name" />
              </div>
              <p v-if="inputNameMessage" class="help is-danger">{{ inputNameMessage }}</p>
            </div>
          </div>
        </div>
         <div class="field is-horizontal">
          <div class="field-label is-normal"></div>
          <div class="field-body">
            <div class="field">
              <div class="control">
                <button class="button is-light" type="submit" v-on:submit="addSeries">Add</button>
              </div>
            </div>
          </div>
        </div>
      </form>

    </div>
  </div>

</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Series, getSeriesList, searchSeriesList, createSeries, SeriesInputData } from '../assets/ts/series';
import { MultiDataResponse } from '../assets/ts/network';

//import SeriesCard from './models/SeriesCard.vue'

const SeriesOverview = defineComponent({
  data() {
    return {
      series: {} as [Series],
      limit: 0,
      size: 0,
      offset: 0,
      page: 1,
      searchTerm: "",      
      inputNameMessage: ""
    }
  },
  components: {
    //SeriesCard
  },
  mounted() {
    this.fetchData();
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
  methods: {
    fetchData() {
      if (this.searchTerm) {
        searchSeriesList(this.searchTerm, this.offset)
        .then((data: MultiDataResponse<Series>) => {
          this.series = data.data;
          this.size = data.size;
          this.limit = data.limit;
        })
        .catch((message) => {
          console.error('Could not fetch series', message);
        });

      } else {
        getSeriesList(this.offset)
        .then((data: MultiDataResponse<Series>) => {
          this.series = data.data;
          this.size = data.size;
          this.limit = data.limit;
        })
        .catch((message) => {
          console.error('Could not fetch series', message);
        });
      }
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
    },
    search(submitEvent: any) {
      //console.log('submitEvent:', submitEvent);
      submitEvent.preventDefault();

      // input validation
      try {
        var searchTerm = submitEvent.target.elements.search.value;
        if (!searchTerm) {
          searchTerm = "";
        }
      } catch (error) {
        console.error(error);
        return;
      }

      this.searchTerm = searchTerm;
      this.fetchData();
    },
    addSeries(submitEvent: any) {
      submitEvent.preventDefault();

      try {
        var name = submitEvent.target.elements.name.value;
        if (!name) {
          this.inputNameMessage = "Missing series name";
          throw "Missing series name"
        }
      } catch (error) {
        console.error(error);
        return;
      }

      const data: SeriesInputData = {
        name: name
      }

      createSeries(data)
        .then(() => {
          console.log('Series created');
          
          // reset form
          this.inputNameMessage = "";          
          submitEvent.target.reset();

          this.fetchData();
        })
        .catch((message) => {
          console.error('Could not create series:', message);
          this.inputNameMessage = message;
        });
       
    }
  }
})

export default SeriesOverview;
</script>

<style lang="scss">
@import '../assets/scss/_variables.scss';

.series-table-link {
  color: $text;
}

nav.pagination {
  font-size: 11pt;
}

nav.pagination button {
  padding-left: 0.8em;
  padding-right: 0.8em;
}
</style>