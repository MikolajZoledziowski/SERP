<template>
  <div id="split-container">
    <div id="graph-container">
      <div id="graph"></div>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3';
  import $ from 'jquery';
  import colorbrewer from 'colorbrewer';
  import LineSegment from './../line-segment';

  export default {

    props: {
      filter:Array,
      config: Object,
      graph: Object,
      maxLineChars: Number,
      wrapChars: Array,
      selected: Object,
      highlighted: Object,
      selectedNodeName: String
    },

    mounted() {
      this.init();
    },

    methods: {
      onNodeSelected(obj) {
        this.$emit('nodeSelected', obj);
      },

      onNodeDeselected(obj) {
        this.$emit('nodeDeselected', obj);
      },

      init() {
        this.drawGraph();

        let self = this;
        $(document).on('click', '.select-object', function() {
          const obj = self.$data.fitProps.graph.data[$(this).data('name')];
          if (obj) {
            self.selectObject(obj);
          }
          return false;
        });

        setTimeout(() => {
          const initNode = this.getMostLinkedNode();
          this.selectObject(initNode);
          this.zoomToNode(initNode);
        });
      },

      drawGraph() {
        let self = this;
        $('#graph').empty();
        this.$data.fitProps.graph.margin = {
          top: 20,
          right: 20,
          bottom: 20,
          left: 20
        };

        let display = $('#graph').css('display');
        $('#graph')
            .css('display', 'block');
            //.css('height', this.$data.fitProps.config.graph.height + 'px');
        this.$data.fitProps.graph.width = $('#graph').width() - this.$data.fitProps.graph.margin.left - this.$data.fitProps.graph.margin.right;
        this.$data.fitProps.graph.height = $('#graph').height() - this.$data.fitProps.graph.margin.top - this.$data.fitProps.graph.margin.bottom;
        $('#graph').css('display', display);

        for (let name in this.$data.fitProps.graph.data) {
          let obj = this.$data.fitProps.graph.data[name];
          obj.positionConstraints = [];
          obj.linkStrength = 1;
        }

        this.$data.fitProps.graph.links = [];
        for (let name in this.$data.fitProps.graph.data) {
          let obj = this.$data.fitProps.graph.data[name];
          for (let depIndex in obj.depends) {
            let link = {
              source: this.$data.fitProps.graph.data[obj.depends[depIndex]],
              target: obj
            };
            link.strength = (link.source.linkStrength || 1)
                * (link.target.linkStrength || 1);
            this.$data.fitProps.graph.links.push(link);
          }
        }
//////////////////////////////////////////////////////////////////////
        this.$data.fitProps.graph.categories = {};
        for (let name in this.$data.fitProps.graph.data) {
          let obj = this.$data.fitProps.graph.data[name];
          let key = obj.type + ':' + (obj.group || '');
          let cat = this.$data.fitProps.graph.categories[key];

          obj.categoryKey = key;
          if (!cat) {
            cat = this.$data.fitProps.graph.categories[key] = {
              key: key,
              type: obj.type,
              typeName: (this.$data.fitProps.config.types[obj.type]
                  ? this.$data.fitProps.config.types[obj.type].short : obj.type),
              group: obj.group,
              count: 0
            };

          }
          cat.count++;
        }
        this.$data.fitProps.graph.categoryKeys = d3.keys(this.$data.fitProps.graph.categories);
        this.$data.fitProps.graph.colors = colorbrewer.Set3[this.$data.fitProps.config.graph.numColors];
        this.$emit('categories', this.$data.fitProps.graph.categoryKeys);
    
        let getColorScale = darkness => {
          return d3.scale.ordinal()
            .domain(this.$data.fitProps.graph.categoryKeys)
            .range(this.$data.fitProps.graph.colors.map(c => {
                return d3.hsl(c).darker(darkness).toString();
            }));
        }

        this.$data.fitProps.graph.strokeColor = getColorScale( 0.7);
        this.$data.fitProps.graph.fillColor = getColorScale(-0.1);

        this.$data.fitProps.graph.nodeValues = d3.values(this.$data.fitProps.graph.data);

        this.$data.fitProps.graph.force = d3.layout.force()
            .nodes(this.$data.fitProps.graph.nodeValues)
            .links(this.$data.fitProps.graph.links)
            .linkStrength(d => { return d.strength; })
            .size([this.$data.fitProps.graph.width, this.$data.fitProps.graph.height])
            .linkDistance(this.$data.fitProps.config.graph.linkDistance)
            .charge(this.$data.fitProps.config.graph.charge)
            .on('tick', e => {
              this.$data.fitProps.graph.numTicks++;



              if (this.$data.fitProps.graph.preventCollisions) {
                this.preventCollisions();
              }

              this.$data.fitProps.graph.line
                  .attr('x1', d => {
                    return d.source.x;
                  })
                  .attr('y1', d => {
                    return d.source.y;
                  })
                  .each(function(d) {

                    let x = d.target.x;
                    let y = d.target.y;
                    let line = new LineSegment(d.source.x, d.source.y, x, y);

                    for (let e in d.target.edge) {
                      let ix = line.intersect(d.target.edge[e].offset(x, y));
                      if (ix.in1 && ix.in2) {
                        x = ix.x;
                        y = ix.y;
                        break;
                      }
                    }

                    d3.select(this)
                        .attr('x2', x)
                        .attr('y2', y);
                  });

              this.$data.fitProps.graph.node.attr('transform', d => {
                return 'translate(' + d.x + ',' + d.y + ')';
              });
            });

        this.$data.fitProps.graph.zoom = d3.behavior.zoom()
            .scaleExtent([0.1, 2])
            .on('zoom', this.onZoom);


        this.$data.fitProps.graph.svgContainer = d3.select('#graph').append('svg')
            .attr('width', this.$data.fitProps.graph.width + this.$data.fitProps.graph.margin.left + this.$data.fitProps.graph.margin.right)
            .attr('height', this.$data.fitProps.graph.height + this.$data.fitProps.graph.margin.top  + this.$data.fitProps.graph.margin.bottom)
            .call(this.$data.fitProps.graph.zoom);

        this.$data.fitProps.graph.svg = this.$data.fitProps.graph.svgContainer
            .append('g')
              .attr('transform', 'translate(' + this.$data.fitProps.graph.margin.left + ',' + this.$data.fitProps.graph.margin.top + ')');
            

        this.$data.fitProps.graph.svg.append('defs').selectAll('marker')
            .data(['end'])
          .enter().append('marker')
            .attr('id', String)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 10)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
          .append('path')
            .attr('d', 'M0,-5L10,0L0,5');

        // adapted from http://stackoverflow.com/questions/9630008
        // and http://stackoverflow.com/questions/17883655

        let glow = this.$data.fitProps.graph.svg.append('filter')
            .attr('x', '-50%')
            .attr('y', '-50%')
            .attr('width', '200%')
            .attr('height', '200%')
            .attr('id', 'blue-glow');

        glow.append('feColorMatrix')
            .attr('type'  , 'matrix')
            .attr('values', 
                  '0 0 0 0  0 '
                + '0 0 0 0  0 '
                + '0 0 0 0  0.7 '
                + '0 0 0 1  0 ');

        glow.append('feGaussianBlur')
            .attr('stdDeviation', 2)
            .attr('result', 'coloredBlur');

        glow.append('feMerge').selectAll('feMergeNode')
            .data(['coloredBlur', 'SourceGraphic'])
          .enter().append('feMergeNode')
            .attr('in', String);

        this.$data.fitProps.graph.legend = this.$data.fitProps.graph.svgContainer
            .append('g')
              .attr('transform', 'translate(' + this.$data.fitProps.graph.margin.left + ',' + this.$data.fitProps.graph.margin.top + ')')
            .append('g')
              .attr('class', 'legend')
              .attr('x', 0)
              .attr('y', 0)
            .selectAll('.category')
              .data(d3.values(this.$data.fitProps.graph.categories))
            .enter().append('g')
              .attr('class', 'category');

        this.$data.fitProps.graph.legendConfig = {
            rectWidth: 12,
            rectHeight: 12,
            xOffset: -10,
            yOffset: 30,
            xOffsetText: 20,
            yOffsetText: 10,
            lineHeight: 15
        };
        this.$data.fitProps.graph.legendConfig.xOffsetText += this.$data.fitProps.graph.legendConfig.xOffset;
        this.$data.fitProps.graph.legendConfig.yOffsetText += this.$data.fitProps.graph.legendConfig.yOffset;

        this.$data.fitProps.graph.legend.append('rect')
            .attr('x', this.$data.fitProps.graph.legendConfig.xOffset)
            .attr('y', (d, i) => {
                return this.$data.fitProps.graph.legendConfig.yOffset + i * this.$data.fitProps.graph.legendConfig.lineHeight;
            })
            .attr('height', this.$data.fitProps.graph.legendConfig.rectHeight)
            .attr('width', this.$data.fitProps.graph.legendConfig.rectWidth)
            .attr('fill', d => {
                return this.$data.fitProps.graph.fillColor(d.key);
            })
            .attr('stroke', d => {
                return this.$data.fitProps.graph.strokeColor(d.key);
            });

        this.$data.fitProps.graph.legend.append('text')
            .attr('x', this.$data.fitProps.graph.legendConfig.xOffsetText)
            .attr('y', (d, i) => {
                return this.$data.fitProps.graph.legendConfig.yOffsetText + i * this.$data.fitProps.graph.legendConfig.lineHeight;
            })
            .text(d => {
                return d.typeName + (d.group ? ': ' + d.group : '');
            });

        /*$('#graph-container').on('scroll', () => {
            this.$data.fitProps.graph.legend.attr('transform', 'translate(0,' + $(this).scrollTop() + ')');
        });*/

        this.$data.fitProps.graph.line = this.$data.fitProps.graph.svg.append('g').selectAll('.link')
            .data(this.$data.fitProps.graph.force.links())
          .enter().append('line')
            .attr('class', 'link');

        this.$data.fitProps.graph.draggedThreshold = d3.scale.linear()
            .domain([0, 0.1])
            .range([5, 20])
            .clamp(true);

        let dragged = d => {
          let threshold = this.$data.fitProps.graph.draggedThreshold(this.$data.fitProps.graph.force.alpha()),
              dx = d.oldX - d.px,
              dy = d.oldY - d.py;
          if (Math.abs(dx) >= threshold || Math.abs(dy) >= threshold) {
            d.dragged = true;
          }
          return d.dragged;
        }

        this.$data.fitProps.graph.drag = d3.behavior.drag()
            .origin(d => { return d; })
            .on('dragstart', d => {
              d.oldX = d.x;
              d.oldY = d.y;
              d.dragged = false;
              d.fixed |= 2;
            })
            .on('drag', d => {
              d.px = d3.event.x;
              d.py = d3.event.y;
              if (dragged(d)) {
                if (!this.$data.fitProps.graph.force.alpha()) {
                  this.$data.fitProps.graph.force.alpha(.025);
                }
              }
            })
            .on('dragend', function(d) {
              if (!dragged(d)) {
                self.selectObject(d, this);
              }
              d.fixed &= ~6;
            });

        /*$('#graph-container').on('click', e => {
          if (!$(e.target).closest('.node').length) {
            this.deselectObject(this.$data.fitProps.selected.obj);
          }
        });*/



        this.$data.fitProps.graph.node = this.$data.fitProps.graph.svg.selectAll('.node')
            .data(this.$data.fitProps.graph.force.nodes())
          .enter().append('g')
            .attr('class', 'node')
            .call(this.$data.fitProps.graph.drag)
            .on('mouseover', d => {
              if (!this.$data.fitProps.selected.obj) {
                if (this.$data.fitProps.graph.mouseoutTimeout) {
                  clearTimeout(this.$data.fitProps.graph.mouseoutTimeout);
                  this.$data.fitProps.graph.mouseoutTimeout = null;
                }
                this.highlightObject(d);
              }
            })
            .on('mouseout', () => {
              if (!this.$data.fitProps.selected.obj) {
                if (this.$data.fitProps.graph.mouseoutTimeout) {
                  clearTimeout(this.$data.fitProps.graph.mouseoutTimeout);
                  this.$data.fitProps.graph.mouseoutTimeout = null;
                }
                this.$data.fitProps.graph.mouseoutTimeout = setTimeout(() => {
                  this.highlightObject(null);
                }, 300);
              }
            });

        this.$data.fitProps.graph.nodeRect = this.$data.fitProps.graph.node.append('rect')
            .attr('rx', 3)
            .attr('ry', 3)
            .attr('stroke', d => {
                return this.$data.fitProps.graph.strokeColor(d.categoryKey);
            })
            .attr('fill', d => {
                return this.$data.fitProps.graph.fillColor(d.categoryKey);
            })
            .attr('width' , 120)
            .attr('height', 30);

        this.$data.fitProps.graph.node.each(function(d) {
          let node = d3.select(this);
          let rect = node.select('rect');
          let lines = self.wrap(d.name);
          let ddy = 1.1;
          let dy = -ddy * lines.length / 2 + .5;

          lines.forEach((line) => {
            let text = node.append('text')
                .text(line)
                .attr('dy', dy + 'em');
            dy += ddy;
          });
        });

        let graphConfig = this.$data.fitProps.config.graph;
        setTimeout(() => {
          this.$data.fitProps.graph.node.each(function(d) {
            let node = d3.select(this);
            let text = node.selectAll('text');
            let bounds = {};
            let first = true;

            text.each(function() {
              let box = this.getBBox();
              if (first || box.x < bounds.x1) {
                bounds.x1 = box.x;
              }
              if (first || box.y < bounds.y1) {
                bounds.y1 = box.y;
              }
              if (first || box.x + box.width > bounds.x2) {
                bounds.x2 = box.x + box.width;
              }
              if (first || box.y + box.height > bounds.y2) {
                bounds.y2 = box.y + box.height;
              }
              first = false;
            }).attr('text-anchor', 'middle');

            const padding = graphConfig.labelPadding;
            const margin = graphConfig.labelMargin;
            const oldWidth = bounds.x2 - bounds.x1;

            bounds.x1 -= oldWidth / 2;
            bounds.x2 -= oldWidth / 2;

            bounds.x1 -= padding.left;
            bounds.y1 -= padding.top;
            bounds.x2 += padding.left + padding.right;
            bounds.y2 += padding.top + padding.bottom;

            node.select('rect')
                .attr('x', bounds.x1)
                .attr('y', bounds.y1)
                .attr('width', bounds.x2 - bounds.x1)
                .attr('height', bounds.y2 - bounds.y1);

            d.extent = {
              left: bounds.x1 - margin.left,
              right: bounds.x2 + margin.left + margin.right,
              top: bounds.y1 - margin.top,
              bottom: bounds.y2 + margin.top  + margin.bottom
            };

            d.edge = {
              left: new LineSegment(bounds.x1, bounds.y1, bounds.x1, bounds.y2),
              right: new LineSegment(bounds.x2, bounds.y1, bounds.x2, bounds.y2),
              top: new LineSegment(bounds.x1, bounds.y1, bounds.x2, bounds.y1),
              bottom: new LineSegment(bounds.x1, bounds.y2, bounds.x2, bounds.y2)
            };
          });

          this.$data.fitProps.graph.numTicks = 0;
          this.$data.fitProps.graph.preventCollisions = false;
          this.$data.fitProps.graph.force.start();
          for (let i = 0; i < this.$data.fitProps.config.graph.ticksWithoutCollisions; i++) {
            this.$data.fitProps.graph.force.tick();
          }
          this.$data.fitProps.graph.preventCollisions = true;
          $('#graph-container').css('visibility', 'visible');

          this.$data.fitProps.graph.zoomElements = d3.selectAll('#graph>svg>g');
        });
      },

      wrap(text) {
        const maxLineChars = this.$data.fitProps.maxLineChars;
        const wrapChars = this.$data.fitProps.wrapChars;
        if (text.length <= maxLineChars) {
          return [text];
        } else {
          for (let k = 0; k < wrapChars.length; k++) {
            let c = wrapChars[k];
            for (let i = maxLineChars; i >= 0; i--) {
              if (text.charAt(i) === c) {
                let line = text.substring(0, i + 1);
                return [line].concat(this.wrap(text.substring(i + 1)));
              }
            }
          }
          return [text.substring(0, maxLineChars)]
              .concat(this.wrap(text.substring(maxLineChars)));
        }
      },

      preventCollisions() {
        let quadtree = d3.geom.quadtree(this.$data.fitProps.graph.nodeValues);

        for (let name in this.$data.fitProps.graph.data) {
          let obj = this.$data.fitProps.graph.data[name];
          let ox1 = obj.x + obj.extent.left;
          let ox2 = obj.x + obj.extent.right;
          let oy1 = obj.y + obj.extent.top;
          let oy2 = obj.y + obj.extent.bottom;

          quadtree.visit((quad, x1, y1, x2, y2) => {
            if (quad.point && quad.point !== obj) {
              // Check if the rectangles intersect
              let p = quad.point;
              let px1 = p.x + p.extent.left;
              let px2 = p.x + p.extent.right;
              let py1 = p.y + p.extent.top;
              let py2 = p.y + p.extent.bottom;
              let ix = (px1 <= ox2 && ox1 <= px2 && py1 <= oy2 && oy1 <= py2);
              if (ix) {
                let xa1 = ox2 - px1; // shift obj left , p right
                let xa2 = px2 - ox1; // shift obj right, p left
                let ya1 = oy2 - py1; // shift obj up   , p down
                let ya2 = py2 - oy1; // shift obj down , p up
                let adj = Math.min(xa1, xa2, ya1, ya2);

                if (adj == xa1) {
                  obj.x -= adj / 2;
                  p.x += adj / 2;
                } else if (adj == xa2) {
                  obj.x += adj / 2;
                  p.x -= adj / 2;
                } else if (adj == ya1) {
                  obj.y -= adj / 2;
                  p.y += adj / 2;
                } else if (adj == ya2) {
                  obj.y += adj / 2;
                  p.y -= adj / 2;
                }
              }
              return ix;
            }
          });
        }
      },

      selectObject(obj, el) {
        let node;
        if (el) {
          node = d3.select(el);
        } else {
          this.$data.fitProps.graph.node.each(function(d) {
            if (d === obj) {
              node = d3.select(el = this)
              return false
            }
          });
        }
        this.deselectObject();
        if (!node || node.classed('selected')) return;
        this.$data.fitProps.selected = { obj, el };
        var t0 = performance.now();
        this.highlightObject(obj,this.value)
        this.highlightLines()
        var t1 = performance.now();
        console.log("Call to doSomething took " + (t1 - t0) + " milliseconds.")
        this.displayNode=[]
        node.classed('selected', true);
        this.onNodeSelected(obj);
        const $graph = $('#graph-container');
        const nodeRect = {
            left: obj.x + obj.extent.left + this.$data.fitProps.graph.margin.left,
            top: obj.y + obj.extent.top + this.$data.fitProps.graph.margin.top,
            width: obj.extent.right - obj.extent.left,
            height: obj.extent.bottom - obj.extent.top
        };

        const graphRect = {
            left: $graph.scrollLeft(),
            top: $graph.scrollTop(),
            width: $graph.width(),
            height: $graph.height()
        };

        if (nodeRect.left < graphRect.left ||
            nodeRect.top < graphRect.top ||
            nodeRect.left + nodeRect.width > graphRect.left + graphRect.width ||
            nodeRect.top + nodeRect.height > graphRect.top + graphRect.height) {

          $graph.animate({
              scrollLeft: nodeRect.left + nodeRect.width / 2 - graphRect.width / 2,
              scrollTop: nodeRect.top + nodeRect.height / 2 - graphRect.height / 2
          }, 500);
        }
      },

      deselectObject(obj) {
        this.$data.fitProps.graph.node.classed('selected', false);
        this.$data.fitProps.selected = {};
        this.highlightObject(null);
        if (obj) {
          this.onNodeDeselected(obj);
        }
      },

      highlightObject(obj,value) {
        let el
        let node
        let nodes = this.$data.fitProps.graph.data;
        let filter = filter = this.filter[this.value-value]
        console.log("filter",filter)
        if (obj) {
          this.$data.fitProps.graph.node.classed('inactive', d => obj !== d);
          this.$data.fitProps.highlighted = obj;
          this.$data.fitProps.graph.node.each(function(d) {
            for(let tmp in obj.dependedOnBy){
              if(d===nodes[obj.dependedOnBy[tmp]]&&(filter.includes(d.categoryKey) || filter.includes("Wszystkie"))){
                node = d3.select(el = this);
                try{
                  node.classed('inactive', false);
                }
                catch(err){
                  console.log("err:",err)
                }
              }
            }
            for(let tmp in obj.depends){
              if(d===nodes[obj.depends[tmp]]&&(filter.includes(d.categoryKey) || filter.includes("Wszystkie"))){
                node = d3.select(el = this);
                try{
                  node.classed('inactive', false);
                }
                catch(err){
                  console.log("err:",err)
                }
              }
            }
        });
        } else {
          if (this.$data.fitProps.highlighted) {
            this.$data.fitProps.graph.node.classed('inactive', false)
          }
          this.$data.fitProps.highlighted = null;
        }
        if(value>1){
          let nodes = this.$data.fitProps.graph.data;
          for(let tmp in obj.dependedOnBy){
            if(filter.includes(nodes[obj.dependedOnBy[tmp]].categoryKey)|| filter.includes("Wszystkie")){
              this.highlightObjectWithoutHide(nodes[obj.dependedOnBy[tmp]],value-1)
            }
          }
          for(let tmp in obj.depends){
            if(filter.includes(nodes[obj.depends[tmp]].categoryKey)|| filter.includes("Wszystkie")){
              this.highlightObjectWithoutHide(nodes[obj.depends[tmp]],value-1)
           }
          }
        }
      },

      highlightLines() {
        let highlightedObject = []
        this.$data.fitProps.graph.line.classed("inactive",true)
        this.$data.fitProps.graph.node.each(function(d) {
          //console.log("name:",d.name)
          if(!d3.select(this).classed('inactive')){
            highlightedObject.push(d.name)
          }
      });
      this.$data.fitProps.graph.line.each(function(d) {
        if(highlightedObject.includes(d.source.name) && highlightedObject.includes(d.target.name)){
          d3.select(this).classed("inactive",false)
        }
      })
      console.log(highlightedObject)
      },

      highlightObjectWithoutHide(obj,value) {

        let el
        let filter
        if(value===0){
          filter = this.filter[this.value-1]
        }else{
          filter = this.filter[this.value-value]
        }
        let node
        let nodes = this.$data.fitProps.graph.data
        var highlightObjectWithoutHide = this.highlightObjectWithoutHide
        let check = this.displayNode

        if (obj && obj !== this.$data.fitProps.highlighted && !this.displayNode.find( e => e === obj.name)) {
          check.push(obj.name)
          if((obj.dependedOnBy.length+obj.depends.length)>1){
            this.$data.fitProps.graph.node.each(function(d) {
              
              if(value===1){
                if ((d.depends.includes(obj.name)||d.dependedOnBy.includes(obj.name))&&(filter.includes(d.categoryKey )||filter.includes("Wszystkie"))){

                  node = d3.select(el = this);
                  try{
                    node.classed('inactive', false);
                    for(let tmp in obj.dependedOnBy){
                      if(filter.includes(nodes[obj.dependedOnBy[tmp]].categoryKey)||filter.includes("Wszystkie")){
                        highlightObjectWithoutHide(nodes[obj.dependedOnBy[tmp]],value-1);
                      }
                    }
                    for(let tmp in obj.depends){
                      if(filter.includes(nodes[obj.depends[tmp]].categoryKey)||filter.includes("Wszystkie")){
                        highlightObjectWithoutHide(nodes[obj.depends[tmp]],value-1);
                      }
                    }
                  }
                  catch(err){
                    console.log("err:",err)
                  }
                  return false
                }
              }
              if(value>1){
                if ((d.depends.includes(obj.name)||d.dependedOnBy.includes(obj.name))&&(filter.includes(d.categoryKey )||filter.includes("Wszystkie"))){
                  node = d3.select(el = this);
                  try{
                    node.classed('inactive', false);
                    for(let tmp in obj.dependedOnBy){

                      if(filter.includes(nodes[obj.dependedOnBy[tmp]].categoryKey)|| filter.includes("Wszystkie")){
                        highlightObjectWithoutHide(nodes[obj.dependedOnBy[tmp]],value-1);
                      }
                    }
                    for(let tmp in obj.depends){

                      if(filter.includes(nodes[obj.depends[tmp]].categoryKey)|| filter.includes("Wszystkie")){
                        highlightObjectWithoutHide(nodes[obj.depends[tmp]],value-1);
                      }
                    }
                  }
                  catch(err){
                    console.log("err:",err)
                  }
                  return false
                }
              }
            });
          }
        }
      },

      getMostLinkedNode() {
        let nodes = this.$data.fitProps.graph.data;
        let mostLinkedNode = null;
        let maxLinks = -Infinity;
        for (let nodeName in nodes) {
          // console.log("nodeName:",nodeName)
          let node = nodes[nodeName];
          let linksCount = node.depends.length + node.dependedOnBy.length;
          if (linksCount > maxLinks) {
            maxLinks = linksCount;
            mostLinkedNode = node;
          }
        }
        return mostLinkedNode;
      },

      selectNodeByName(nodeName) {
        if (this.$data.fitProps.graph.data[nodeName] != undefined) {
          this.selectObject(this.$data.fitProps.graph.data[nodeName]);
        }
      },

      limitVisibleObjects(value) {//TODO: Implement BFS to extract levels of neighbour
        if(value!==99999){
          this.value = value
          this.$data.fitProps.graph.node.classed('force-visible', false);
          this.$data.fitProps.graph.line.classed('force-visible', false);
          //usunąć mierzenie czasu
          var t0 = performance.now();
          this.highlightObject(this.fitProps.selected.obj,value)
          this.highlightLines()
          var t1 = performance.now();
          console.log("Call to doSomething took " + (t1 - t0) + " milliseconds.")
          this.displayNode=[]
        }
        else{
          this.$data.fitProps.graph.node.classed('force-visible', true);
          this.$data.fitProps.graph.line.classed('force-visible', true);
        }
      },

      onZoom() {
        this.$data.fitProps.graph.svg
            .attr('transform', 'translate(' + d3.event.translate + ')scale(' + d3.event.scale + ')');
      },

      zoomToNode(node) {
        const scale = this.$data.fitProps.graph.zoom.scale();
        const translate = [// FIXME
          (this.$data.fitProps.graph.width / 2) - (node.x * scale),
          (window.innerHeight / 2) - (node.y * scale)
        ];
        
        this.$data.fitProps.graph.svg.transition().duration(750)
            .call(this.$data.fitProps.graph.zoom.translate(translate).scale(scale).event);
      }
    },

    data() {
      return {
        value:1,
        displayNode:[],
        fitProps: {
          graph: this.graph,
          config: this.config,
          maxLineChars: 26,
          wrapChars: ' /_-.'.split(''),
          selected: {},
          highlighted: null
        }
      };
    }

  }
</script>


<style>
  #split-container {
    height: 100%;
    width: 100%;
  }

  #graph-container {
    width: 100%;
    height: 100%;
    overflow-y: hidden;
    visibility: hidden;
  }

  #graph {
    cursor: move;
  }

  .link {
    fill: none;
    stroke: #666;
    stroke-width: 1px;
    opacity: .7;
    marker-end: url(#end);
    cursor: pointer;
    transition: opacity 250ms;
    -webkit-transition: opacity 250ms;
    -moz-transition: opacity 250ms;
  }

  marker#end {
    fill: #666;
    stroke: #666;
    stroke-width: 1px;
  }

  .node rect {
    stroke-width: 1px;
    cursor: pointer;
    transition: opacity 250ms;
    -webkit-transition: opacity 250ms;
    -moz-transition: opacity 250ms;
  }

  .node text {
    fill: #000;
    font: 6px sans-serif;
    pointer-events: none;
  }

  .node.selected rect {
    filter: url(#blue-glow);
  }

  body.firefox .node.selected rect {
    filter: none;
    stroke: #000;
    stroke-width: 2px;
  }

  .link.inactive {
    display: none;
    /*opacity: .2;*/
  }
  .node.inactive rect,
  .node.inactive text {
    display: none;
    /*opacity: .1;*/
  }

  .link.inactive.force-visible {
    display: block;
    /*opacity: .2;*/
  }
  .node.inactive.force-visible  rect,
  .node.inactive.force-visible  text {
    display: block;
    /*opacity: .1;*/
  }

  .node.inactive.selected rect,
  .node.inactive.selected text {
      opacity: .6;
  }

  .legend {
    position: fixed;
  }

  .legend .category rect {
    stroke-width: 1px;
  }

  .legend .category text {
    fill: #000;
    font: 10px sans-serif;
    pointer-events: none;
  }

</style>
