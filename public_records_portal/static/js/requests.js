// Manage the display of the record request table.
(function($) {

  Query = Backbone.Model.extend({

    defaults:
    {
      page: 0,
      per_page: 15,
      total_requests: 0,
      offset: 0
    },

    prev_page: function ()
    {
      this.set({
        "offset": this.get("offset") - this.get("per_page")
      })
    },

    next_page: function ()
    {
      this.set({
        "offset": this.get("offset") + this.get("per_page")
      })
    }

  })

  Request = Backbone.Model.extend({})

  RequestSet = Backbone.Collection.extend({

    model: Request,

    initialize: function( models, options )
    {
      this._query = options.query
      this._query.on( "change", this.build, this )
    },

    url: function ()
    {
      return "/api/request"
    },

    build: function ()
    {
      console.log("Fetching a new result set.")
      var query = JSON.stringify({"limit": this._query.get("per_page"), "offset": this._query.get("offset")})
      console.log(query)
      this.fetch({
        data: { "q": query },
        dataType: "json",
        contentType: "application/json"
      });
    },

    parse: function ( response )
    {
      return response.objects
    }

  })

  // Smaller filter query control box that sits off to the side.
  FilterBox = Backbone.View.extend({

    initialize: function ()
    {
      this.model.on( "change", this.render, this )
    },

    render: function ()
    {
      var variables = {
        current_results: this.model.per_page,
        total_requests: this.model.total_requests
      }
      var template = _.template( $("#sidebar_template").html(), variables );
      this.$el.html( template );
    },

    events:
    {
      "click #filterbox input[type=checkbox]": "change_search",
      "change #filterbox .selectpicker": "change_search"
    },

    change_search: function ()
    {
      this.model.set( { "total_requests": this.model.get( "total_requests" ) + 10 } )
    }

  });

  SearchResults = Backbone.View.extend({

    initialize: function ()
    {
      this.collection.on( "add", this.render, this )
    },

    render: function ()
    {
      console.log("Rendering new results.")
      var vars = { requests: this.collection.toJSON() }
      var template = _.template( $("#search_results_template").html(), vars )
      this.$el.html( template )
    },

    events:
    {
      "click .pagination .prev": "prev",
      "click .pagination .next": "next"
    },

    prev: function ()
    {
      this.model.prev_page()
    },

    next: function ()
    {
      this.model.next_page()
    }

  });

  var query = new Query();
  var request_set = new RequestSet([], { query: query });
  var filter_box = new FilterBox({ el: $("#sidebar_container"), model: query });
  var search_results = new SearchResults({
    el: $("#search_results_container"),
    model: query,
    collection: request_set
  })

  query.set({ "page": 1 })

})(jQuery);
