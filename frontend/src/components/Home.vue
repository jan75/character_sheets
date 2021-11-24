<template>
  <SeriesOverview />
</template>


<script lang="ts">
import { defineComponent } from 'vue';
import SeriesOverview from './SeriesOverview.vue'

const Home = defineComponent({
  components: {
    SeriesOverview
  }
})

export default Home;
</script>
