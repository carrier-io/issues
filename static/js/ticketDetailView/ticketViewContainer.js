const TicketViewContainer = {
    props: ["engagement", "ticket"],
    emits: ['updated'],
    components: {
        'header-container': TicketHeaderContainer,
        'description-container': TicketDetailContainer,
        'attachments-container': TicketAttachmentsContainer,
        'comments-container': TicketCommentsContainer,
        'activity-container': TicketActivityContainer,
    },
    watch:{
        engagement(){
            this.adjustTableHeight()
            this.setTopHeightChangeObserver()
        },
    },
    mounted() {
        this.adjustTableHeight()
    },
    methods: {
        topElementHeight(){
            topHeight = $('.eng-header-element').outerHeight(true)
            topHeight = topHeight? topHeight: 0
            return topHeight;
        },

        setTopHeightChangeObserver(){
            resizeObserver = new ResizeObserver(entries => {
                this.adjustTableHeight();
            });
            const elements = document.getElementsByClassName('eng-header-element')
            for (const element of elements) {
                resizeObserver.observe(element);
            }
        },

        propagateEvent(data){
            newTicket = {...this.ticket}
            Object.assign(newTicket, data)
            this.$emit('updated', newTicket)
        },

        close(){
            this.$emit('updated', null)
        },
        
        adjustTableHeight() {
            getExcessPixels = ()=>{
                sidebar = document.getElementById('engagement-wrapper')
                container = this.$refs.table
                return Math.abs(sidebar.getBoundingClientRect().bottom - container.getBoundingClientRect().bottom)
            }
            const totalHeight = window.innerHeight;
            const navbarHeight = $('nav').outerHeight(true);
            topHeight = $('.eng-header-element').outerHeight(true)
            topHeight = topHeight? topHeight: 0
            const table = this.$refs.table;
            const remainingHeight = totalHeight - topHeight - navbarHeight;
            table.style.height = `${remainingHeight}px`;
            this.$nextTick(() => {
                excessivePixels = getExcessPixels();
                table.style.height = `${remainingHeight - excessivePixels}px`
            });
        },
    },
    template: `
        <div class="card my-3" style="margin: 0px">
            <div class="card-body" style="padding: 0px">
                <div class="ticket-view" ref="table">
                    
                    <header-container
                        :ticket="ticket"
                        @updated="propagateEvent"
                        @close="close"
                    ></header-container>

                    <div class="detail-body">
                        <description-container
                            :ticket=ticket
                            @updated="propagateEvent"
                        >
                        </description-container>
                    
                        <attachments-container
                            :ticket=ticket
                        >
                        </attachments-container>

                        <comments-container
                            :ticket=ticket
                        >
                        </comments-container>

                        <activity-container
                            v-if="ticket"
                            :ticket=ticket
                        >
                        </activity-container>
                    </div>
                </div>
            </div>
        </div>
    `
}
