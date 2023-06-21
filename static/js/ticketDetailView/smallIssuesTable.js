function getDisplayStatusName(status){
    return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase().trim().replaceAll('_', ' ')
}

function customTitleFormatter(value, row){
    if (value.length>60)
        value = value.slice(0, 60) + '...'    
    return `
    <div class="ticket-cell">
        <div class="ticket-title">
            <div class="title">
               ${value}
            </div>
            <span class="ticket-type">
                ${row.type}
            </span>
        </div>
        <div class="card-detail-row">
            <div class="param">
                <i class="icon__18x18 icon-severity__18 gray-bg"></i> 
                <span class="param-text">${getDisplayStatusName(row.severity)}</span>
            </div>
            <div class="param">
                <i class="icon__18x18 icon-status__18 gray-bg"></i> 
                <span class="param-text">
                    ${getDisplayStatusName(row.state.value)}
                </span>
            </div>
        </div>
    </div>
    `
}

const SmallIssuesTable = {
    props: [
        'engagement',
        'pageNumber',
        'ticket',
    ],
    emits: ['updated'],
    components: {
        'ticket-creation-modal': TicketCreationModal,
        'filter-toolbar-container': FilterToolbarContainer,
    },
    data() {
        return {
            url: issues_api_url,
            issues_url: issues_api_url,
            preFilterMap: {},
            table_id: "#small-issues-table",
            itemsCount: 0,

            previousScrollTop: 0,
            isLoadingTop: false,
            isLoadingBottom: false,
            page: 1,
            pageSize: 10,
            needsPrependScroll: false,
            loadedPages: new Set(),
        }
    },
    watch:{
        ticket(value, oldValue){            
            if (oldValue==null && value!=null){
                this.page = this.$props.pageNumber
                this.loadedPages.clear()
                this.loadedPages.add(this.page)
                $(this.table_id).bootstrapTable('refresh', {
                    url: this.preparedUrl
                })
            }
        },
        pageNumber(value){
            this.page = value
        }
    },
    computed:{
        preparedUrl(){
            offset = (this.page-1) * this.pageSize
            querySign = this.issues_url.includes('?')? "&": "?"
            return this.issues_url + querySign + 'offset=' + offset + '&limit=' + this.pageSize;
        },
        maxPage(){
            const arr = Array.from(this.loadedPages)
            return Math.max(...arr)
        },

        minPage(){
            const arr = Array.from(this.loadedPages)
            return Math.min(...arr)
        },

    },
    mounted(){
        this.setClickEvent();

        $(this.table_id).on('load-success.bs.table', (e, data) => {
            this.loadedPages.add(this.page)
            this.itemsCount = data.total;
            $(this.table_id).bootstrapTable('hideLoading');
            this.selectAndScrollToTicket()
            self = this
            $(`div#smTableContainer .fixed-table-body`).on('scroll', function() {
                scrollPosition = $(this).scrollTop();
                // Check if scrolling up by comparing the previous and current scroll positions
                if (scrollPosition < self.previousScrollTop) {
                    tableOffsetTop = $(this).find('tbody tr:first').offset().top;
                    // Check if the scroll position is near the top of the table
                    if (scrollPosition <= tableOffsetTop && !self.isLoadingTop) {
                        // Decrement the page number
                        nextPage = self.minPage - 1
                        if (nextPage > 0){
                            self.page = nextPage
                            // Load more data at the top
                            self.loadMoreData('top');
                        }
                  }
                } else {
                  tableHeight = $(this).height();
                  tableScrollHeight = $(this).find('tbody').get(0).scrollHeight;
      
                  // Check if the scroll position is near the bottom of the table
                  if (scrollPosition + tableHeight >= tableScrollHeight - 50 && !self.isLoadingBottom) {
                    // Increment the page number
                    maxPageCount = Math.floor(self.itemsCount/self.pageSize) + 1
                    nextPage = self.maxPage + 1
                    if(nextPage <= maxPageCount){
                        self.page = nextPage
                        // Load more data at the bottom
                        self.loadMoreData('bottom');
                    }
                  }
                }
      
                // Update the previous scroll position
                self.previousScrollTop = scrollPosition;
            });

            $(this.table_id).on('post-body.bs.table', function() {
                if (self.needsPrependScroll){
                    $(self.table_id).bootstrapTable('scrollTo', {value: self.pageSize, unit: 'rows'})
                    self.needsPrependScroll = false
                }
            });
        });
        
        $(this.table_id).on('click-row.bs.table', (e, row) => {
            this.$emit('updated', row)
        })
    },  
    methods: {

        getRowIndexById(itemId) {
            const data = $(this.table_id).bootstrapTable('getData');
            console.log(data)
            for (let i = 0; i < data.length; i++) {
              if (data[i].id === itemId) {
                return i;
              }
            }
            return -1; 
        },
          

        selectAndScrollToTicket(){
            if (!this.ticket)
                return
            $(`${this.table_id} tbody tr[data-uniqueid="${this.ticket.id}"]`).click()
            position = this.getRowIndexById(this.ticket.id)
            $(this.table_id).bootstrapTable('scrollTo', {value: position, unit: 'rows'})
        },

        // Table events
        setClickEvent() {
            vm = this
            $(this.table_id).on('click', `tbody tr:not(.no-records-found)`, function(e){
                $('.title').css('color', '#32325D')
                $(this).find('.title').css('color', '#5933C6')
                $(this).addClass('highlight').siblings().removeClass('highlight');
            });
        },

        // Table methods
        refreshTable(queryUrl, reload=true){
            this.issues_url = queryUrl
            if(reload){
                $(this.table_id).bootstrapTable("refresh", {
                    url: this.issues_url
                })
            }
        },

        loadMoreData(direction){
            // Show the loading indicator
            $(this.table_id).bootstrapTable('showLoading');

            if (direction === 'top') {
              this.isLoadingTop = true;
            } else if (direction === 'bottom') {
              this.isLoadingBottom = true;
            }
        
            axios.get(this.preparedUrl)
            .then(response => {
                if (direction === 'top') {
                    this.needsPrependScroll = true
                   $(this.table_id).bootstrapTable('prepend', response.data.rows);
                } else if (direction === 'bottom') {
                   $(this.table_id).bootstrapTable('append', response.data.rows);
                }
                this.loadedPages.add(this.page)
                $(this.table_id).bootstrapTable('hideLoading');
                this.isLoadingTop = false;
                this.isLoadingBottom = false;

                $(`${this.table_id} tbody tr[data-uniqueid="${this.ticket?.id}"]`).click()
            })
            .catch(error => {
                console.log('Error loading data:', error);
            });
        },
    },
    template: `
        <div class="card mt-3 mr-3 card-table-sm table-scroll">
            <filter-toolbar-container
                variant="slot"
                :url="url"
                resp_data_field="rows"
                :table_id="table_id"
                button_class="btn-sm btn-icon__sm btn-secondary"
                :list_items="['severity', 'type', 'source', 'status', 'tags']"
                :pre_filter_map="preFilterMap"
                @applyFilter="refreshTable"
            >
                <template #title>
                    <h4>Tickets</h4>  
                </template>

                <template #before>
                    <div class="custom-input custom-input_search__sm mr-2 position-relative">
                        <input
                            id="search-bar"
                            type="text"
                            placeholder="Search">
                        <img src="/issues/static/ico/search.svg" class="icon-search position-absolute">
                    </div>
                </template>
                
                <template #dropdown_button><i class="fa fa-filter"></i></template>
                
                <template #after>
                    <ticket-creation-modal
                        :engagement="engagement"
                    >
                    </ticket-creation-modal>
                </template>

            </filter-toolbar-container>

            <div class="card-body pt-0">
                <div class="small-table-container" id="smTableContainer">
                    <table class="table table-borderless fixed-table-body"
                        id="small-issues-table"
                        :data-url="preparedUrl"
                        data-toggle="table"
                        data-unique-id="id"
                        data-cache="false"
                    >
                        <thead class="thead-light">
                            <tr>
                                <th style="height: auto;" data-field="title" data-formatter="customTitleFormatter">Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="padding: 24px 20px">
                <span class="font-h5 text-gray-600">{{itemsCount}} items</span>
            </div>
        </div>
    `
}