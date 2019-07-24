import Vue from 'vue'
import Router from 'vue-router'
import SERP from '@/components/SERP'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'SERP',
      component: SERP
    },

  ]
})
