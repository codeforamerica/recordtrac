// Manage the display of the record request table.
(function($) {

  Query = Backbone.Model.extend({

    defaults:
    {
      page: 0,
      per_page: 10,
      num_results: 0
    },

    prev_page: function ()
    {
      this.set({ page: this.get("page") - 1 })
    },

    next_page: function ()
    {
      this.set({ page: this.get("page") + 1 })
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
      this.fetch({
        data: {
          "results_per_page": this._query.get("per_page"),
          "page": this._query.get("page")
        },
        dataType: "json",
        contentType: "application/json"
      });
    },

    parse: function ( response )
    {
      this._query.set({
        "num_results": response.num_results,
        "page": response.page
      })
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
      this.collection.on( "sync", this.render, this )
    },

    render: function (event_name)
    {
      console.log("Rendering new results on event: " + event_name)
      var vars = { requests: this.collection.toJSON() }
      var template = _.template( $("#search_results_template").html(), vars )
      this.$el.html( template )
    },

    events:
    {
      "click .pagination .prev": "prev",
      "click .pagination .next": "next",
      "change #per-page": "update_per_page"
    },

    prev: function ()
    {
      this.model.prev_page()
    },

    next: function ()
    {
      this.model.next_page()
    },

    update_per_page: function ( event )
    {
      this.model.set("per_page", event.target.value)
    }

  });

  query = new Query();
  request_set = new RequestSet([], { query: query });
  var filter_box = new FilterBox({ el: $("#sidebar_container"), model: query });
  var search_results = new SearchResults({
    el: $("#search_results_container"),
    model: query,
    collection: request_set
  })

  query.set({ "page": 1 })

})(jQuery);
