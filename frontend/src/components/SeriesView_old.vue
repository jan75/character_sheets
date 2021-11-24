<template>

  <div class="columns">
    <div class="column">
      <h1 class="title">{{ name }}</h1>
    </div>
  </div>

  <div class="columns">
    <div class="column is-three-quarters">

      <div class="columns is-multiline is-1 is-variable"> 
        <p v-if="selectedEntries.length == 0">Add entries from the table to the right</p>
        <div class="column is-3" v-for="entry in selectedEntries" v-bind:key="entry.id">
          <div class="entry-card" v-on:click="unsetSelected(entry)">
            <div class="columns">
              <div class="column">
                <div class="level">
                  <div class="level-left">
                    <h3>{{ entry.name }}</h3>
                  </div>
                  <div class="level-right">
                    <span class="tag is-dark">{{ entry.entrytype.name }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="columns">
              <div class="column">
                <p>Date: {{ entry.date }}</p>
                <p>Series: {{ entry.series.name }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
    <div class="column">

      <table class="entry-table table is-hoverable is-fullwidth">
        <thead>
          <tr>
            <td>#</td>
            <th>Entry</th>
            <th>Date</th>
            <th>Type</th>            
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr class="selected-entry" v-for="entry in selectedEntries" v-bind:key="entry.id">
            <td>{{ entry.order_in_series }}</td>
            <td>{{ entry.name }}</td>
            <td>{{ entry.date }}</td>
            <td>{{ entry.entrytype.name }}</td>            
            <td><button class="button is-small" type="button" v-on:click="setSelected(entry)">Add</button></td>
          </tr>
          <tr v-for="entry in unselectedEntries" v-bind:key="entry.id">
            <td>{{ entry.order_in_series }}</td>
            <td>{{ entry.name }}</td>
            <td>{{ entry.date }}</td>
            <td>{{ entry.entrytype.name }}</td>            
            <td><button class="button is-small" type="button" v-on:click="setSelected(entry)">Add</button></td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>

</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { MultiDataResponse } from '../assets/ts/network';
import { Series, getSeries, getSeriesEntries } from '../assets/ts/series';
import { Entry } from '../assets/ts/entries';
import { EntryType } from '@/assets/ts/entrytypes';

class SelectableEntry implements Entry {
  id: number
  name: string
  date: string
  order_in_series: number
  series: Series
  entrytype: EntryType
  selected: boolean

  constructor(entry: Entry) {
    this.id = entry.id
    this.name = entry.name;
    this.date = entry.date;
    this.order_in_series = entry.order_in_series;
    this.series = entry.series;
    this.entrytype = entry.entrytype;
    this.selected = false;
  }

}

const SeriesView = defineComponent({
  data() {
    return {
      name: "",
      id: Number(this.$route.params.id),
      entries: {
        data: [] as SelectableEntry[],
        size: 0,
        offset: 0,
        limit: 0,
        page: 1
      }
    }
  },
  created() {
    this.fetchSeries();
    this.fetchEntries();
  },
  computed: {
    selectedEntries(): SelectableEntry[] {
      return this.entries.data.filter(entry => entry.selected);
    },
    unselectedEntries(): SelectableEntry[] {
      return this.entries.data.filter(entry => !entry.selected);
    }
  },
  methods: {
    fetchSeries() {
      if (this.id) {
        getSeries(this.id)
        .then((series: Series) => {
          this.name = series.name;
        })
        .catch((message) => {
          console.error('Could not fetch series, invalid series?', message);
          this.$router.push({name: '404'});
        });
      } else {
        console.error('id is undefined');
        this.$router.push('404');
      }
    },
    fetchEntries() {
      if (this.id) {
        getSeriesEntries(this.id, this.entries.offset)
        .then((entries: MultiDataResponse<Entry>) => {
          console.log('Entries fetched:', entries);

          let selectableEntries: SelectableEntry[] = [];
          entries.data.forEach(function (item, ) {     
            selectableEntries.push(new SelectableEntry(item));
          });

          this.entries.data = selectableEntries;
        })
        .catch((message) => {
          console.error('Could not fetch entries, invalid series?', message);
          this.$router.push({name: '404'})
        });
      } else {
        console.error('id is undefined');
        this.$router.push('404');
      }
    },
    setSelected(selectableEntry: SelectableEntry): void {
      console.log('setting selected:', selectableEntry);
      if (!selectableEntry.selected) {
        selectableEntry.selected = true;
      } else {
        console.error('Entry is already selected');
      }
    },
    unsetSelected(selectableEntry: SelectableEntry): void {
      console.log('unsetting selected:', selectableEntry);
      if (selectableEntry.selected) {
        selectableEntry.selected = false;
      } else {
        console.error('Entry is not yet selected');
      }
    }
  }
})

export default SeriesView;
</script>

<style lang="scss">
div.entry-card {
  //padding: 0.8em;
  margin-left: 0.2em;
  margin-right: 0.2em;
  margin-top: 0.4em;
  margin-bottom: 0.4em;
  padding-left: 0.8em;
  padding-right: 0.8em;
  
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 5% 5% 5% 5%;
  cursor: pointer;
}

div.entry-card:hover {
  margin-left: 0.2em;
  margin-right: 0.2em;
  margin-top: 0.4em;
  margin-bottom: 0.4em;
  padding-left: 0.8em;
  padding-right: 0.8em;
  
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 5% 5% 5% 5%;
  cursor: pointer;
}

table.entry-table {
  //cursor: pointer;
}

table.entry-table .selected-entry {
  background-color: red;
}

table.entry-table .selected-entry:hover {
  background-color: darkred;
}
</style>