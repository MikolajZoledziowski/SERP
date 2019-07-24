<template>
    <v-layout row wrap>
    <v-flex xs6 sm6 md6 lg6>
             <v-text-field
            label="Regular"
            v-model = query
          ></v-text-field>
    </v-flex>
    <v-btn @click='search'>Wyszukaj</v-btn>
      <v-flex xs12 sm12 md12 lg12>
        <ul class= 'list'>
          <li v-for="link in links">
            <a :href='link'>{{ link}}</a>
          </li>
        </ul>  
    </v-flex>
    </v-layout>

</template>

<script>
  import axios from 'axios'

  export default {

    mounted() {

    },
    methods: {
      search(){
        console.log('query', this.query)
        let formData = new FormData()
        formData.set("query", this.query)
        axios.post('/api/core/get_links', formData).then(response =>{
          this.links = response.data.items
        })
      }
    },

    data() {
      return {
        query: '',
        links: [],
      }
    }
  }
</script>


<style>
  .list {
    font-size: 15px;
  }

</style>
