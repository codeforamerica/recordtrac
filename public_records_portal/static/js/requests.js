(function(){

window.App = {
};

App.Router = Backbone.Router.extend({
});
Router = new App.Router;
Backbone.history.start({pushState: true})

})();


// Manage the display of the record request table.
(function($) {

  Query = Backbone.Model.extend({
    defaults: {
      open:               true,
      closed:             false,
      due_soon:           true,
      overdue:            true,
      mine_as_poc:        true,
      mine_as_helper:     true,
      sort_column:        "id",
      sort_direction:     "desc",
      search_term:        "",
      min_due_date:       "",
      max_due_date:       "",
      min_request_date:   "",
      max_request_date:   "",
      requester_name:     "",
      department:         "",
      page_number:        1,
      more_results:       false,
      start_index:        0,
      end_index:          0,
      filters:            ['closed', 'sort_column', 'sort_direction', 'min_request_date', 'max_request_date', 'department', 'page_number', 'search_term'],
      staff_only_filters: ['open', 'due_soon', 'overdue', 'mine_as_poc', 'mine_as_helper', 'min_due_date', 'max_due_date', 'requester_name']
    },

    toggle: function(attribute_name) {
      this.set(attribute_name, !(this.get(attribute_name)));
    },

    prev_page: function() {
      if (this.get("page_number") > 1) {
        this.set({ page_number: parseInt(this.get("page_number")) - 1 })
      }
    },

    next_page: function() {
      this.set({ page_number: parseInt(this.get("page_number")) + 1 })
    },

    switch_sort_direction: function() {
      if (this.get('sort_direction') === 'desc') {
        this.set('sort_direction', 'asc');
      } else {
        this.set('sort_direction', 'desc');
      }
    }
  })

  Request = Backbone.Model.extend({})

  RequestSet = Backbone.Collection.extend({
    model: Request,

    initialize: function(models, options) {
      this._query = options.query
      this._query.on("change", this.build, this);
      this._filters = this._query.get('filters')
      var that = this
      if ($('#user_id').val() != 'None') // If user is logged in, initialize staff filters
      {
        this._filters = this._filters.concat(this._query.get('staff_only_filters'))
      }

      var filter_query = function(){
        this.url = function(url){
          return decodeURI(url)
        }
      }
      var filter_query = new filter_query
       var vars = filter_query.url(window.location.search.substring(1)).split('&')
        $.each(vars, function(index, variable) {
          var filter = decodeURIComponent(variable.split("=")[0])
          var value = decodeURIComponent(variable.split("=")[1])
          if (value != 'undefined') {
            that._query.set(filter, value)
            if (filter == 'search_term')
            {
              SearchField.set_search_term
            }
          }
        })

      this._query.on( "change", this.build, this )
    },

    url: function() {
      return "/custom/request"
    },

    build: function() {
      var route_url = ""
      var that = this
      var data_params = {}

      $.each(this._filters, function( index, filter ) {
         value = that._query.get(filter)
          if (value != 'undefined') {
                data_params[filter] = value
                if (route_url == "")
                {
                  route_url += "requests?"
                }
                else
                {
                  route_url += "&"
                }
                route_url = route_url + encodeURIComponent(filter) + "=" + encodeURIComponent(value)
          }
      });

      Router.navigate(route_url)

      this.fetch({
        data: data_params,
        dataType: "json",
        contentType: "application/json"
      });
    },

    parse: function(response) {
      this._query.set({
        "more_results": response.more_results,
        "start_index":  response.start_index,
        "end_index":    response.end_index,
        "num_results":  response.num_results
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
      "click #mine_as_poc":    "toggle_mine_as_poc",
      "click #mine_as_helper": "toggle_mine_as_helper",
      "click #open":           "toggle_open",
      "click #due_soon":       "toggle_due_soon",
      "click #overdue":        "toggle_overdue",
      "click #closed":         "toggle_closed"
    },

    toggle_mine_as_poc: function() {
      this.model.toggle('mine_as_poc');
    },

    toggle_mine_as_helper: function() {
      this.model.toggle('mine_as_helper');
    },

    toggle_open: function() {
      this.model.toggle("open");
    },

    toggle_due_soon: function() {
      this.model.toggle("due_soon");
    },

    toggle_overdue: function() {
      this.model.toggle("overdue");
    },

    toggle_closed: function() {
      this.model.toggle('closed');
    }
  });

  SearchField = Backbone.View.extend({
    initialize: function() {
      this.render();
      this.model.on('change:search_term', this.render, this);
    },

    template: _.template($("#search_field_template").html()),

    render: function() {
      this.$el.html(this.template({ search_term: this.model.get('search_term') }));
      if (this.should_be_focused) {
        this.$el.find('#search').focus().val('').val(this.model.get('search_term'));
      }
    },

    events: {
      "keyup #search_term": "set_search_term",
      "focus input":              "remember_focus"
    },

    set_search_term: _.debounce(function(event) {
      this.model.set('search_term', event.target.value);
    }, 300),

    remember_focus: function() {
      this.should_be_focused = true;
    }
  });

  RequesterName = Backbone.View.extend({

    initialize: function() {
      this.render();
      this.model.on('change:requester_name', this.render, this);
    },

    template: _.template($("#requester_name_template").html()),

    render: function() {
      this.$el.html(this.template({ requester_name: this.model.get('requester_name') }));
      if (this.should_be_focused) {
        this.$el.find('#requester_name').focus().val('').val(this.model.get('requester_name'));
      }
    },

    events: {
      "keyup #requester_name": "set_requester_name",
      "focus input":              "remember_focus"
    },

    set_requester_name: _.debounce(function(event) {
      this.model.set('requester_name', event.target.value);
    }, 300),

    remember_focus: function() {
      this.should_be_focused = true;
    }

  });

  DepartmentSelector = Backbone.View.extend({
    initialize: function() {
      this.render();
      this.model.on('change:department', this.render, this);
    },

    render: function() {
      var template = _.template($("#department_selector_template").html(), this.model.attributes);
      this.$el.html(template);
    },

    events: {
      "change select": "set_department"
    },

    set_department: function(event) {
      this.model.set('department', event.target.value)
    }
  });

  var DateFilter = Backbone.View.extend({
    initialize: function(options) {
      this.title = options.title;
      this.min_field = options.min_field;
      this.max_field = options.max_field;
      this.render();
      this.model.on('change', this.render, this);
    },

    template: _.template($('#date_filter_template').html()),

    render: function() {
      var for_template = {
        title: this.title,
        min_value: this.model.get(this.min_field),
        max_value: this.model.get(this.max_field)
      }

      this.$el.html(this.template(for_template));
      this.$el.find('.min_field').datepicker();
      this.$el.find('.max_field').datepicker();
    },

    events: {
      'change .min_field': 'update_min',
      'change .max_field': 'update_max',
      'click .all_dates': 'clear_dates'
    },

    update_min: function(event) {
      this.model.set(this.min_field, event.target.value);
    },

    update_max: function(event) {
      this.model.set(this.max_field, event.target.value);
    },

    clear_dates: function() {
      this.model.set(this.min_field, "");
      this.model.set(this.max_field, "");
    }
  });

  SearchResults = Backbone.View.extend({
    initialize: function() {
      this.collection.on("sync", this.render, this);
    },

    template: _.template($("#search_results_template").html()),

    render: function() {
      this.$el.html(this.template(_.extend({ 'requests': this.collection.toJSON() }, this.model.attributes)));
      this.$el.find('#' + this.model.attributes.sort_column).addClass(this.model.attributes.sort_direction);
    },

    events: {
      "click .pagination .prev": "prev",
      "click .pagination .next": "next",
      "click th.sortable": "sort"
    },

    prev: function() {
      this.model.prev_page();
    },

    next: function() {
      this.model.next_page();
    },

    sort: function(event) {
      var column_to_sort = event.target.id;

      if (column_to_sort === this.model.get('sort_column')) {
        // If there's a click on the current column, flip the sort direction.
        this.model.switch_sort_direction();
      } else {
        // Otherwise we should default to a descending sort.
        this.model.set('sort_direction', 'desc');
      }

      this.model.set('sort_column', column_to_sort);
    }
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

  var requester_name = new RequesterName({
    el: $("#requester_name_container"),
    model: query
  });

  var department_selector = new DepartmentSelector({
    el: $("#department_selector_container"),
    model: query
  });

  var request_date = new DateFilter({
    el: $("#request_date_container"),
    model: query,
    min_field: 'min_request_date',
    max_field: 'max_request_date',
    title: 'Request Date'
  });

  var due_date = new DateFilter({
    el: $("#due_date_container"),
    model: query,
    min_field: 'min_due_date',
    max_field: 'max_due_date',
    title: 'Due Date'
  });

  var search_results = new SearchResults({
    el: $("#search_results_container"),
    model: query,
    collection: request_set
  })

  request_set.fetch();

})(jQuery);
