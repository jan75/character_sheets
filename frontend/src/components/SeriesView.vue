<template>

  <div class="columns">
    <div class="column">
      <h1 class="title">{{ name }}</h1>
    </div>
  </div>

  <div class="columns">
    <div class="column is-two-thirds">

      <form class="field has-addons character-search" v-on:submit="searchCharacter">
        <div class="control is-expanded">
          <input class="input" type="text" name="search" />
        </div>
        <div class="control">
          <button class="button" type="submit" v-on:submit="searchCharacter">Search</button>
        </div>
      </form>

      <div class="columns is-multiline">
        <div class="column is-4" v-for="character in characters.data" v-bind:key="character.id">
          <h4 class="character-title title is-4">{{ character.name }}</h4>
          <div class="character-tidbit">
            <p>Tidbit 1</p>
          </div>
          <div class="character-tidbit">
            <p>Longer character information, might be a bit more background info and therefore go across multiple lines.</p>
          </div>
        </div>
      </div>

    </div>
    <div class="column">

      <form class="field has-addons entries-search" v-on:submit="searchEntries">
        <div class="control is-expanded">
          <input class="input" type="text" name="search" />
        </div>
        <div class="control">
          <button class="button" type="submit" v-on:submit="searchEntries">Search</button>
        </div>
      </form>

      <table class="entry-table table is-fullwidth">
        <thead>
          <tr>
            <th>#</th>
            <th>Entry</th>
            <th>Date</th>
            <th>Type</th>            
          </tr>
        </thead>
        <tbody>
          <tr class="selected-entry" v-for="entry in selectedEntries.data" v-bind:key="entry.id" v-on:click="unsetSelected(entry)">
            <td>{{ entry.order_in_series }}</td>
            <td>{{ entry.name }}</td>
            <td>{{ entry.date }}</td>
            <td>{{ entry.entrytype.name }}</td>            
          </tr>
        </tbody>
      </table>

      <table class="entry-table table is-fullwidth">
        <thead>
          <tr>
            <th>#</th>
            <th>Entry</th>
            <th>Date</th>
            <th>Type</th>            
          </tr>
        </thead>
        <tbody>
          <tr class="unselected-entry" v-for="entry in unselectedEntries.data" v-bind:key="entry.id" v-on:click="setSelected(entry)">
            <td>{{ entry.order_in_series }}</td>
            <td>{{ entry.name }}</td>
            <td>{{ entry.date }}</td>
            <td>{{ entry.entrytype.name }}</td>         
          </tr>
        </tbody>
      </table>
    </div>

  </div>

</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { MultiDataResponse } from '../assets/ts/network';
import { Series, getSeries, getSeriesEntries, getSeriesCharacters } from '../assets/ts/series';
import { Entry } from '../assets/ts/entries';
import { EntryType } from '@/assets/ts/entrytypes';
import { Character } from '@/assets/ts/characters';

class SelectableEntry implements Entry {
  id: number
  name: string
  date: string
  order_in_series: number
  series: Series
  entrytype: EntryType
  selected: boolean

  constructor(entry: Entry) {
    this.id = entry.id;
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
      selectedEntries: {
        data: [] as SelectableEntry[],
        size: 0,
        offset: 0,
        limit: 0,
        page: 1
      },
      entriesSearchTerm: "",
      unselectedEntries: {
        data: [] as SelectableEntry[],
        size: 0,
        offset: 0,
        limit: 0,
        page: 1
      },
      characterSearchTerm: "",
      characters: {
        data: [] as Character[],
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
    this.fetchCharacters();
  },
  computed: {
    /*
    selectedEntries(): SelectableEntry[] {
      return this.selectedEntries.data;
    },
    unselectedEntries(): SelectableEntry[] {
      return this.unselectedEntries.data;
      //return this.unselectedEntries.data.filter(entry => !entry.selected);
    }
    */
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
        if (this.entriesSearchTerm) {
          //searchSeriesEntries(this.id, this.entriesSearchTerm, this.unselectedEntries.offset)

        } else {
          getSeriesEntries(this.id, this.unselectedEntries.offset)
            .then((entries: MultiDataResponse<Entry>) => {
            console.log('Entries fetched:', entries);

            let selectableEntries: SelectableEntry[] = [];
            entries.data.forEach(function (item, ) { 
              console.log(item);
              selectableEntries.push(new SelectableEntry(item));
            });

            selectableEntries.forEach((item, index) => {
              if (this.selectedEntries.data.find(obj => {
                obj.id == item.id;
              })) {
                // entry already in selected entries, skip
                console.info('Fetched entry already in selected entries. Skipping...');
                selectableEntries.splice(index, 1);
              }
            })

            this.unselectedEntries.data = selectableEntries;
            this.unselectedEntries.limit = entries.limit;
            this.unselectedEntries.offset = entries.offset;
            this.unselectedEntries.size = entries.size;
          })
        .catch((message) => {
          console.error('Could not fetch entries, invalid series?', message);
        });
        }
        
      } else {
        console.error('id is undefined');
        this.$router.push('404');
      }
    },
    fetchCharacters() {
      if (this.id) {
        getSeriesCharacters(this.id, this.characters.offset)
          .then((characters: MultiDataResponse<Character>) => {
            console.log('Characters fetched:', characters);

            this.characters.data = characters.data;
            this.characters.limit = characters.limit;
            this.characters.offset = characters.offset;
            this.characters.size = characters.size;
          })
          .catch((message) => {
            console.error('Could not fetch entries, invalid series?', message);
          })
      } else {
        console.error('id is undefined');
        this.$router.push('404');
      }
    },
    setSelected(selectableEntry: SelectableEntry): void {
      console.log('setting selected:', selectableEntry);
      if (!selectableEntry.selected) {
        selectableEntry.selected = true;
        this.selectedEntries.data.push(selectableEntry);
        const index = this.unselectedEntries.data.indexOf(selectableEntry, 0);
        this.unselectedEntries.data.splice(index, 1);
      } else {
        console.error('Entry is already selected');
      }
    },
    unsetSelected(selectableEntry: SelectableEntry): void {
      console.log('unsetting selected:', selectableEntry);
      if (selectableEntry.selected) {
        selectableEntry.selected = false;
        this.unselectedEntries.data.push(selectableEntry);
        const index = this.selectedEntries.data.indexOf(selectableEntry, 0);
        this.selectedEntries.data.splice(index, 1);
      } else {
        console.error('Entry is not yet selected');
      }
    },
    searchCharacter(submitEvent: any) {
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

      this.characterSearchTerm = searchTerm;
      this.fetchCharacters();
    },
    searchEntries(submitEvent: any) {
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

      this.entriesSearchTerm = searchTerm;
      this.fetchEntries();
    },
  }
})

export default SeriesView;
</script>

<style lang="scss">
table.entry-table td {
  cursor: pointer;
}

table.entry-table .unselected-entry {
  //background-color: rgb(200, 200, 200);
}

table.entry-table .unselected-entry:hover {
  background-color: rgb(200, 200, 200);
}

table.entry-table .selected-entry {
  background-color: rgb(200, 200, 200);
}

table.entry-table .selected-entry:hover {
  background-color: rgb(175, 175, 175);
}

h4.character-title {
  border-bottom: 2px solid #cccccc;
  padding-bottom: 7px;
}

div.character-tidbit {
  border-bottom: 1px solid #cccccc;
  margin-top: 5px;
  margin-bottom: 5px;
  padding-top: 5px;
  padding-bottom: 5px;
}
</style>