import { createMemoryHistory, createRouter } from 'vue-router';

import HomeView from './views/HomeView.vue';
import LoginView from './views/LoginView.vue';
import AdminLayout from './panels/AdminLayout.vue';

import FdBaseView from './views/FdBaseView.vue';
import RdBaseView from './views/RdBaseView.vue';
import LogsView from './views/LogsView.vue';
import TgAccountsView from './views/TgAccountsView.vue';
import PushListView from './views/PushListView.vue';
import ProxyView from './views/ProxyView.vue';


const routes = [
    {
      path: '/', 
      meta: {requiresAuth: true}, 
      component: AdminLayout,
      children: [
        {
          name: 'settings',
          path: 'settings',
          component: HomeView,
          meta: {requiresAuth: true}
        },
        {
          name: 'rd-base',
          path: 'rd-base',
          component: RdBaseView,
          meta: {requiresAuth: true}
        },
        {
          name: 'fd-base',
          path: 'fd-base',
          component: FdBaseView,
          meta: {requiresAuth: true}
        },
        {
          name: 'logs',
          path: 'logs',
          component: LogsView,
          meta: {requiresAuth: true}
        },
        {
          name: 'telegram_accounts',
          path: 'telegram_accounts',
          component: TgAccountsView,
          meta: {requiresAuth: true}
        },
        {
          name: 'push_list',
          path: 'push_list',
          component: PushListView,
          meta: {requiresAuth: true}
        },
        {
          name: 'proxy',
          path: 'proxy',
          component: ProxyView,
          meta: {requiresAuth: true}
        },
      ]
    },
    {
      path: '/login', 
      component: LoginView
    },
    {
      path: '/:catchAll(.*)',
      name: 'NotFound',
      component: AdminLayout, 
    },
];




export const router = createRouter({
    history: createMemoryHistory(import.meta.env.BASE_URL),
    routes
});

router.beforeEach((to, from, next) => {
    const userData = JSON.parse(localStorage.getItem('user'));
  
    if(to.matched.some(record => record.meta.requiresAuth) && !userData){
      next('/login');
    } else {
      next();
    }
  
  });