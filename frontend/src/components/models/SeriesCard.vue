<template>
  <div class="card">
    <div class="card-content">
      <div class="content">
        <p>{{ name }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

const SeriesCard = defineComponent({
  props: {
    id: Number,
    name: String,
    entryNames: [String]
  }
})

export default SeriesCard;
</script>