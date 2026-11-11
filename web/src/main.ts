import { mount } from 'svelte';
import './theme/theme.css';
import App from './App.svelte';
import { loadTierListData } from './contract/load';

const target = document.getElementById('app');

if (!target) {
  throw new Error('Missing #app mount point in template.html');
}

mount(App, { target, props: { data: loadTierListData() } });
