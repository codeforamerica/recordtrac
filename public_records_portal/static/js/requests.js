// Manage the display of the record request table.
(function($) {

  Query = Backbone.Model.extend({

    defaults:
    {
      search_term: "",
      page_number: 1, // Using an attribute called 'page' makes weird things happen here. JFYI.
      open: false,
      due_soon: false,
      overdue: false,
      closed: false,
      mine_as_poc: false,
      mine_as_helper: false,
      requester_name: "",
      department: "",
      more_results: false,
      start_index: 0,
      end_index: 0
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
      this.fetch({
        data: this._query.attributes,
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
    initialize: function() {
      this.render();
      this.model.on('change', this.render, this);
    },

    render: function() {
      var template = _.template($("#sidebar_template").html(), this.model.attributes);
      this.$el.html(template);
    },

    events: {
      "click #open":             "toggle_open",
      "click #due_soon":         "toggle_due_soon",
      "click #overdue":          "toggle_overdue",
      "click #closed":           "toggle_closed",
      "keyup #requester_name":   "set_requester_name",
      "click #my_requests":      "toggle_my_requests",
      "change #department_name": "set_department",
      "change #request_status":  "set_status"
    },

    toggle: function(attribute_name) {
      this.model.set(attribute_name, !(this.model.get(attribute_name)));
    },

    toggle_open: function() {
      this.toggle("open");
    },

    toggle_due_soon: function() {
      this.toggle("due_soon");
    },

    toggle_overdue: function() {
      this.toggle("overdue");
    },

    toggle_closed: function() {
      this.toggle('closed');
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

  SearchField = Backbone.View.extend({
    events: {
      "keyup #search": "set_search_term"
    },

    set_search_term: _.debounce(function(event) {
      this.model.set('search_term', event.target.value);
    }, 300)
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
        "id_icon": this.model.get("id"),
        "text_icon": this.model.get("text"),
        "received_icon": this.model.get("date_created"),
        "due_icon": this.model.get("due_date")
      }

      var data = _.extend(vars, this.model.get_icon, this.model.attributes);
      var template = _.template( $("#search_results_template").html(), data )
      this.$el.html( template )

    },

    events:
    {
      "click .pagination .prev": "prev",
      "click .pagination .next": "next",
      "click #headings th.sortable": "sort"
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
      var sort_attribute = event.target.id
      if (sort_attribute == "")
      {
        sort_attribute = event.target.parentNode.id
      }
      this.model.set_sort(sort_attribute)
    }
  });

  var query = new Query();
  var request_set = new RequestSet([], { query: query });
  var filter_box = new FilterBox({
    el: $("#sidebar_container"),
    model: query
  });
  var search_field = new SearchField({
    el: $("#search_field"),
    model: query
  });
  var search_results = new SearchResults({
    el: $("#search_results_container"),
    model: query,
    collection: request_set
  })

  query.set({ "page": 1 })

})(jQuery);
