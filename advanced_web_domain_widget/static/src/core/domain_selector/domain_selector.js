/** @odoo-module **/

import { Domain } from "@web/core/domain";
import { DomainSelectorRootNodeBits, DomainSelectorRootNodeBits2 } from "./domain_selector_root_node";
import { Component, useState, onWillUpdateProps } from "@odoo/owl";

const COMPANY_DOMAIN = `["|", ("company_id", "=", False), ("company_id", "in", [0])]`;

export class DomainSelectorBits extends Component {
    setup() {
        this.nextNodeId = 0;
        this._isUpdating = false;

        this.state = useState({
            showCompanyFilterCheckbox: this.getShowCompanyFilterCheckbox(this.props),
            includeCompany: false,
            cleanDomain: '[]',
        });

        // Initialize
        const initialClean = this.extractCleanDomain(this.props.value);
        this.state.cleanDomain = initialClean.cleanDomain;
        this.state.includeCompany = initialClean.hasCompanyFilter;

        // Handle props updates - synchronize state with props
        onWillUpdateProps((nextProps) => {
            // Update visibility of company filter toggle whenever props change
            this.state.showCompanyFilterCheckbox = this.getShowCompanyFilterCheckbox(nextProps);
            if (!this._isUpdating && nextProps.value !== this.props.value) {
                const result = this.extractCleanDomain(nextProps.value);
                this.state.cleanDomain = result.cleanDomain;
                // Do NOT update state.includeCompany to preserve user intent
            }
        });
    }

    getShowCompanyFilterCheckbox(props) {
        // If the current model is res.company, do not show the company filter toggle
        return !(props && props.resModel === "res.company");
    }

    extractCleanDomain(domainString) {
        try {
            const domain = new Domain(domainString);
            const domainList = domain.toList();

            const hasCompanyFilter = this.hasCompanyFilter(domainList);

            let cleanDomain;
            if (hasCompanyFilter) {
                const cleanedList = this.removeAllCompanyFilters(domainList);
                cleanDomain = this.normalizeDomain(cleanedList);
            } else {
                cleanDomain = domainString;
            }

            return {
                cleanDomain: cleanDomain,
                hasCompanyFilter: hasCompanyFilter
            };
        } catch (_e) {
            return {
                cleanDomain: domainString,
                hasCompanyFilter: false
            };
        }
    }

    hasCompanyFilter(domainList) {
        for (let i = 0; i < domainList.length - 2; i++) {
            if (domainList[i] === '|' &&
                Array.isArray(domainList[i + 1]) &&
                Array.isArray(domainList[i + 2])) {
                const [field1, op1, val1] = domainList[i + 1];
                const [field2, op2, val2] = domainList[i + 2];

                if (field1 === 'company_id' && op1 === '=' && val1 === false &&
                    field2 === 'company_id' && op2 === 'in' &&
                    Array.isArray(val2) && val2.length === 1 && val2[0] === 0) {
                    return true;
                }
            }
        }
        return false;
    }

    removeAllCompanyFilters(domainList) {
        const result = [];
        let i = 0;

        while (i < domainList.length) {
            if (i < domainList.length - 2 &&
                domainList[i] === '|' &&
                Array.isArray(domainList[i + 1]) &&
                Array.isArray(domainList[i + 2])) {

                const [field1, op1, val1] = domainList[i + 1];
                const [field2, op2, val2] = domainList[i + 2];

                if (field1 === 'company_id' && op1 === '=' && val1 === false &&
                    field2 === 'company_id' && op2 === 'in' &&
                    Array.isArray(val2) && val2.length === 1 && val2[0] === 0) {
                    i += 3;
                    // Remove preceding & operator
                    if (result.length > 0 && result[result.length - 1] === '&') {
                        result.pop();
                    }
                    continue;
                }
            }

            result.push(domainList[i]);
            i++;
        }

        return result;
    }

    normalizeDomain(domainList) {
        // Remove stray operators (e.g., '&' or '|' with insufficient operands)
        if (domainList.length === 0) {
            return '[]';
        }
        // Flatten and deduplicate domain list to avoid nested operators or duplicate
        // conditions that can appear after programmatic combination (see company filter flow).
        const flattenAndDedup = (list) => {
            const out = [];
            const isSameCond = (a, b) => {
                if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
                for (let i = 0; i < a.length; i++) {
                    if (Array.isArray(a[i]) && Array.isArray(b[i])) {
                        if (a[i].length !== b[i].length) return false;
                        for (let j = 0; j < a[i].length; j++) {
                            if (a[i][j] !== b[i][j]) return false;
                        }
                    } else if (a[i] !== b[i]) {
                        return false;
                    }
                }
                return true;
            };

            for (let i = 0; i < list.length; i++) {
                const item = list[i];
                // Skip duplicate consecutive operators
                if (typeof item === 'string' && (item === '&' || item === '|')) {
                    if (out.length === 0) {
                        // don't start with an operator
                        continue;
                    }
                    const prev = out[out.length - 1];
                    if (prev === item) {
                        continue;
                    }
                    // If previous is an operator and current is operator, skip current
                    if (typeof prev === 'string') {
                        continue;
                    }
                    out.push(item);
                    continue;
                }

                // For condition arrays, avoid inserting the same condition twice in a row
                if (Array.isArray(item)) {
                    const prev = out[out.length - 1];
                    if (Array.isArray(prev) && isSameCond(prev, item)) {
                        continue;
                    }
                }

                out.push(item);
            }

            // If result starts with an operator and only one condition follows, remove operator
            if (out.length === 2 && typeof out[0] === 'string' && Array.isArray(out[1])) {
                return [out[1]];
            }

            return out;
        };
        // If only one condition remains and it's preceded by an operator, remove the operator
        const cleaned = flattenAndDedup(domainList);
        if (cleaned.length === 0) {
            return '[]';
        }
        if (cleaned.length === 1 && Array.isArray(cleaned[0])) {
            return new Domain([cleaned[0]]).toString();
        }

        // Validate the domain
        try {
            return new Domain(cleaned).toString();
        } catch (_e) {
            // If invalid, return the first valid condition or '[]'
            const conditions = cleaned.filter(item => Array.isArray(item) && item.length === 3);
            return conditions.length > 0 ? new Domain([conditions[0]]).toString() : '[]';
        }
    }

    buildTree() {
        try {
            const domain = new Domain(this.state.cleanDomain);
            const domainList = domain.toList();

            const ctx = {
                parent: null,
                index: 0,
                domain: domainList,
                get currentElement() {
                    return ctx.domain[ctx.index];
                },
                next() {
                    ctx.index++;
                },
                getFullDomain: () => {
                    return rootNode.computeDomain().toString();
                },
            };

            const rootNode = this.makeRootNode(ctx);
            ctx.parent = rootNode;
            this.traverseNode(ctx);

            return ctx.parent;
        } catch (_e) {
            return false;
        }
    }

    applyCompanyFilterToDomain(baseDomain) {
        try {
            // Always start with a clean domain by removing any existing company filters
            let domainList = new Domain(baseDomain).toList();
            domainList = this.removeAllCompanyFilters(domainList);
            const cleanDomain = this.normalizeDomain(domainList);

            if (!this.state.includeCompany) {
                return cleanDomain;
            }

            // Apply company filter
            const company = new Domain(COMPANY_DOMAIN);
            const combined = Domain.and([new Domain(cleanDomain), company]);
            // Sanitize the combined domain to avoid nested operators / duplicates
            try {
                const combinedList = new Domain(combined.toString()).toList();
                const sanitized = this.normalizeDomain(combinedList);
                return sanitized;
            } catch (_e) {
                return combined.toString();
            }
        } catch (_e) {
            return baseDomain;
        }
    }

    updateDomainAndProps(newCleanDomain) {
        this._isUpdating = true;

        // Normalize the new domain to ensure validity
        let domainList;
        try {
            domainList = new Domain(newCleanDomain).toList();
        } catch (_e) {
            domainList = [];
        }
        this.state.cleanDomain = this.normalizeDomain(domainList);

        // Apply company filter if toggle is ON
        const finalDomain = this.applyCompanyFilterToDomain(this.state.cleanDomain);

        // Update props
        this.props.update(finalDomain);

        setTimeout(() => {
            this._isUpdating = false;
        }, 0);
    }

    toggleApplyCompanyFilter() {
        this._isUpdating = true;
        // Flip local state according to user intent
        this.state.includeCompany = !this.state.includeCompany;

        // Rebuild domain from cleanDomain to ensure correct company filter application
        let domainList;
        try {
            domainList = new Domain(this.state.cleanDomain).toList();
        } catch (_e) {
            domainList = [];
        }
        domainList = this.removeAllCompanyFilters(domainList);
        const cleanDomain = this.normalizeDomain(domainList);
        const finalDomain = this.applyCompanyFilterToDomain(cleanDomain);

        // Push to props
        this.props.update(finalDomain);

        setTimeout(() => {
            this._isUpdating = false;
        }, 0);
    }

    traverseNode(ctx) {
        if (ctx.index < ctx.domain.length) {
            if (typeof ctx.currentElement === "string" && ["&", "|"].includes(ctx.currentElement)) {
                this.traverseBranchNode(ctx);
            } else {
                this.traverseLeafNode(ctx);
            }
        }
    }

    traverseBranchNode(ctx) {
        if (ctx.parent.type !== "branch" || ctx.parent.operator !== ctx.currentElement) {
            const node = this.makeBranchNode(ctx, ctx.currentElement, []);
            ctx.parent.operands.push(node);
            ctx = Object.assign(Object.create(ctx), { parent: node });
        }
        ctx.next();
        this.traverseNode(ctx);
        ctx.next();
        this.traverseNode(ctx);
    }

    traverseLeafNode(ctx) {
        const condition = ctx.currentElement;
        const [leftOperand, operator, rightOperand] = condition;
        const node = this.makeLeafNode(ctx, operator, [leftOperand, rightOperand]);
        ctx.parent.operands.push(node);
    }

    makeBranchNode(ctx, operator, operands) {
        const updateDomain = () => {
            const baseDomain = ctx.getFullDomain();
            this.updateDomainAndProps(baseDomain);
        };
        const makeFakeNode = this.makeFakeNode.bind(this);

        return {
            type: "branch",
            id: this.nextNodeId++,
            operator,
            operands,
            computeDomain() {
                return Domain.combine(
                    this.operands.map((operand) => operand.computeDomain()),
                    this.operator === "&" ? "AND" : "OR"
                );
            },
            update(operator) {
                this.operator = operator;
                updateDomain();
            },
            insert(newNodeType) {
                const newNode = makeFakeNode(ctx, newNodeType);
                const operands = ctx.parent.operands;
                operands.splice(operands.indexOf(this) + 1, 0, newNode);
                updateDomain();
            },
            delete() {
                const operands = ctx.parent.operands;
                operands.splice(operands.indexOf(this), 1);
                updateDomain();
            },
        };
    }

    makeLeafNode(ctx, operator, operands) {
        const updateDomain = () => {
            const baseDomain = ctx.getFullDomain();
            this.updateDomainAndProps(baseDomain);
        };
        const makeFakeNode = this.makeFakeNode.bind(this);

        return {
            type: "leaf",
            id: this.nextNodeId++,
            operator,
            operands,
            computeDomain() {
                return new Domain([[this.operands[0], this.operator, this.operands[1]]]);
            },
            update(changes) {
                if ("fieldName" in changes) {
                    this.operands[0] = changes.fieldName;
                }
                if ("operator" in changes) {
                    this.operator = changes.operator;
                }
                if ("value" in changes) {
                    this.operands[1] = changes.value;
                }
                updateDomain();
            },
            insert(newNodeType) {
                const newNode = makeFakeNode(ctx, newNodeType);
                const operands = ctx.parent.operands;
                operands.splice(operands.indexOf(this) + 1, 0, newNode);
                updateDomain();
            },
            delete() {
                const operands = ctx.parent.operands;
                operands.splice(operands.indexOf(this), 1);
                updateDomain();
            },
        };
    }

    makeRootNode(ctx) {
        const updateDomain = (...args) => {
            if (args.length > 0 && typeof args[0] === "string") {
                this.updateDomainAndProps(args[0]);
            } else {
                this.props.update(...args);
            }
        };
        const makeFakeNode = this.makeFakeNode.bind(this);

        return {
            type: "root",
            id: this.nextNodeId++,
            operator: "&",
            operands: [],
            computeDomain() {
                return Domain.combine(
                    this.operands.map((operand) => operand.computeDomain()),
                    "AND"
                );
            },
            update(newValue, fromDebug) {
                if (typeof newValue === "string") {
                    updateDomain(newValue, fromDebug);
                } else if (this.operands.length) {
                    this.operands[0].update(newValue);
                }
            },
            insert(newNodeType) {
                const newNode = makeFakeNode(ctx, newNodeType);
                if (ctx.parent) {
                    const operands = ctx.parent.operands;
                    operands.splice(operands.indexOf(this) + 1, 0, newNode);
                } else {
                    this.operands.push(newNode);
                }
                updateDomain(ctx.getFullDomain());
            },
            delete() { },
        };
    }

    makeFakeNode(ctx, type) {
        const [field, op, value] = this.props.defaultLeafValue;
        if (type === "branch") {
            return this.makeBranchNode(ctx, ctx.parent.operator === "&" ? "|" : "&", [
                this.makeLeafNode(ctx, op, [field, value]),
                this.makeLeafNode(ctx, op, [field, value]),
            ]);
        } else {
            return this.makeLeafNode(ctx, op, [field, value]);
        }
    }
}

Object.assign(DomainSelectorBits, {
    template: "advanced_web_domain_widget._DomainSelectorBits",
    components: {
        DomainSelectorRootNodeBits,
    },
    props: {
        className: { type: String, optional: true },
        resModel: String,
        value: String,
        debugValue: { type: String, optional: true },
        readonly: { type: Boolean, optional: true },
        update: { type: Function, optional: true },
        isDebugMode: { type: Boolean, optional: true },
        defaultLeafValue: { type: Array, optional: true },
    },
    defaultProps: {
        readonly: true,
        update: () => { },
        isDebugMode: false,
        defaultLeafValue: ["id", "=", 1],
    },
});

export class DomainSelectorBits2 extends DomainSelectorBits { }

DomainSelectorBits2.components = {
    ...DomainSelectorBits.components,
    DomainSelectorRootNodeBits: DomainSelectorRootNodeBits2
};