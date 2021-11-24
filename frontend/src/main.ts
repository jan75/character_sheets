import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import './assets/scss/main.scss'

import App from './App.vue'
import Home from './components/Home.vue'
import SeriesView from './components/SeriesView.vue'
import ErrorNotFound from './components/errors/ErrorNotFound.vue'
//import SeriesView from './components/SeriesView.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/series/:id',
        name: 'series',
        component: SeriesView
    },
    {
        path: '/404',
        name: '404',
        component: ErrorNotFound
    }
]

const router = createRouter({    
    history: createWebHistory(),
    routes: routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')