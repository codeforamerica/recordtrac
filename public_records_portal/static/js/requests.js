// Manage the display of the record request table.
(function($) {

  Query = Backbone.Model.extend({

    defaults:
    {
      search_term: "",
      page_number: 1,
      // Using an attribute called 'page' makes weird things happen here. JFYI.
      is_closed: true,
      my_requests: false,
      department: "",
      more_results: false,
      start_index: 0,
      end_index: 0,
      status: ""
    },

    prev_page: function ()
    {
      if (this.get("page_number") > 1) {
      this.set({ page_number: this.get("page_number") - 1 })
      }
    },

    next_page: function ()
    {
      this.set({ page_number: this.get("page_number") + 1 })
    },

    toggle_sort_order: function()
    {
      this.set({sort_by_ascending: !this.get("sort_by_ascending")})
    },
    set_icon: function(attribute)
    {
     if (this.get("sort_by_ascending") == true)
      {
        this.set(attribute, "icon icon-sort-up")
      } 
      else
      {
        this.set(attribute, "icon icon-sort-down")
      }
    },
    reset_sort: function(attribute)
    {
      var attributes=["id", "text", "due_date", "date_created"];
      for (var i in attributes)
      {
        if (attributes[i] != attribute)
        {
          this.set(attributes[i], "icon icon-sort")
        }
      }
    },
    set_sort: function(attribute)
    {
      this.reset_sort(attribute)
      if (this.get("sort_by_attribute") == attribute) 
      {
         this.toggle_sort_order()
      }
      else 
      {
          this.set({sort_by_attribute: attribute})
          this.set({sort_by_ascending: false})
      }
      this.set_icon(attribute)
      this.set({ page_number: 1 })
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
      return "/custom/request"
    },
    build: function ()
    {

      var data_params = {
        "page": this._query.get("page_number"),
        "is_closed": this._query.get("is_closed"),
        "requester_name": this._query.get("requester_name"),
        "my_requests": this._query.get("my_requests"),
        "ascending": this._query.get("sort_by_ascending"),
        "sort_by": this._query.get("sort_by_attribute")
      }

      var search_term = this._query.get("search_term")
      if ( search_term !== "" )
      {
        data_params["search"] = search_term
      }
      var department = this._query.get("department")
      if ( department != "")
      {
        data_params["department"] = department
      }
      var status = this._query.get("status")
      if ( status != "")
      {
        data_params["status"] = status
      }

      this.fetch({
        data: data_params,
        dataType: "json",
        contentType: "application/json"
      });
    },

    parse: function ( response )
    {
      this._query.set({
        "more_results": response.more_results,
        "start_index": response.start_index,
        "end_index": response.end_index,
        "page": response.page,
        "num_results": response.num_results
      })
      return response.objects
    }

  })

  // Smaller filter query control box that sits off to the side.
  FilterBox = Backbone.View.extend({

    initialize: function ()
    {
      this.render()
    },

    render: function ()
    {
      var vars = {
        "is_closed": this.model.get( "is_closed" ),
        "requester_name": this.model.get("requester_name"),
        "my_requests": this.model.get("my_requests"),
        "department": this.model.get("department"),
        "status": this.model.get("status"),
        "page_number": this.model.get("page_number"),
        "num_results": this.model.get("num_results")
      }
      var template = _.template( $("#sidebar_template").html(), vars );
      this.$el.html( template );
    },

    events:
    {
      "click #is_closed": "toggle_show_closed",
      "keyup #requester_name": "set_requester_name",
      "click #my_requests": "toggle_my_requests",
      "change #department_name": "set_department",
      "change #request_status": "set_status"
    },

    toggle_show_closed: function ( event )
    {
      this.model.set( {
        "is_closed": !( this.model.get( "is_closed" ) )
      } )
      this.model.set({ page_number: 1 })
    },
    toggle_my_requests: function ( event )
    {
      this.model.set( {
        "my_requests": !( this.model.get( "my_requests" ) )
      } )
      this.model.set({ page_number: 1 })
    },
    set_department: function (event)
    {
      this.model.set("department", event.target.value)
      this.model.set({ page_number: 1 })
    },
    set_status: function (event)
    {
      this.model.set("status", event.target.value)
      this.model.set({ page_number: 1 })
    },
    set_requester_name: _.debounce(function (event)
    {
      this.model.set("requester_name", event.target.value)
      this.model.set({ page_number: 1 })
    }, 500)    

  });


  SearchResults = Backbone.View.extend({

    initialize: function ()
    {
      this.model.reset_sort("")
      this.collection.on( "sync", this.render, this )
    },

    render: function (event_name)
    {
      var vars = { 
        requests: this.collection.toJSON(),
        "page_number": this.model.get("page_number"),
        "num_results": this.model.get("num_results"),
        "more_results": this.model.get("more_results"),
        "start_index": this.model.get("start_index"),
        "end_index": this.model.get("end_index"),
        "id_icon": this.model.get("id"),
        "text_icon": this.model.get("text"),
        "received_icon": this.model.get("date_created"),
        "due_icon": this.model.get("due_date")
      }

      var data = _.extend(vars, this.model.get_icon);
      var template = _.template( $("#search_results_template").html(), data )
      this.$el.html( template )

    },

    events:
    {
      "click .pagination .prev": "prev",
      "click .pagination .next": "next",
      "click #headings div": "sort",
    },

    prev: function ()
    {
      this.model.prev_page()
    },

    next: function ()
    {
      this.model.next_page()
    },
    sort: function(event)
    {   
      this.model.set_sort(event.target.id)
    }
  });

  SearchField = Backbone.View.extend({

    initialize: function ()
    {
      this.render()
    },

    render: function ()
    {
      var template = _.template( 
        $("#search_field_template").html(), 
          { current_query: this.model.get("search_term") 
          }
        )

      this.$el.html( template )
    },

    events:
    {
      "keyup #search input": "set_search_term"
    },

    set_search_term: _.debounce(function ( event )
    {
      this.model.set( "search_term", event.target.value )
      this.model.set({ page_number: 1 })
    }, 300)

  });
 


  var query = new Query();
  var request_set = new RequestSet([], { query: query });
  var filter_box = new FilterBox({
    el: $("#sidebar_container"),
    model: query
  });
  var search_field = new SearchField({
    el: $("#search_field_container"),
    model: query
  });
  var search_results = new SearchResults({
    el: $("#search_results_container"),
    model: query,
    collection: request_set
  })

  query.set({ "page": 1 })

})(jQuery);
