<template>

  <content class="main-content">
    <div class="container">
      <router-view />
    </div>
  </content>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

const App = defineComponent({})

export default App;
</script>

<style lang="scss">
.main-header {
  margin-bottom: 20px;
}
</style>
