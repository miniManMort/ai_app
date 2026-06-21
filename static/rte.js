/* Simple Rich Text Editor (RTE) - no external libraries
   Usage:
     - Add class "rte" to any <textarea> you want converted.
     - Include this script and the accompanying CSS.
     - The original <textarea> is hidden and will be updated with HTML
       on form submit so server receives the formatted content.
*/
(function () {
  // Text formatting utilities using modern Selection/Range APIs
  var RTE = {
    // Get the current selection and range
    getSelection: function () {
      return {
        selection: window.getSelection(),
        range: window.getSelection().rangeCount > 0 ? window.getSelection().getRangeAt(0) : null
      };
    },

    // Apply inline formatting (bold, italic, underline, strikethrough)
    applyInlineFormat: function (tag) {
      var sel = window.getSelection();
      if (!sel.rangeCount || sel.toString().length === 0) return;

      var range = sel.getRangeAt(0);
      var span = document.createElement(tag);
      
      try {
        range.surroundContents(span);
        sel.removeAllRanges();
        sel.addRange(range);
      } catch (e) {
        // If surroundContents fails (complex selection), use extract and wrap
        var fragment = range.extractContents();
        span.appendChild(fragment);
        range.insertNode(span);
        sel.removeAllRanges();
        sel.addRange(range);
      }
    },

    // Unwrap inline formatting
    removeInlineFormat: function (tag) {
      var sel = window.getSelection();
      if (!sel.rangeCount) return;

      var range = sel.getRangeAt(0);
      var commonAncestor = range.commonAncestorContainer;
      var parent = commonAncestor.nodeType === Node.TEXT_NODE ? commonAncestor.parentNode : commonAncestor;

      while (parent && parent.tagName !== tag && parent.className !== 'rte-editor') {
        parent = parent.parentNode;
      }

      if (parent && parent.tagName === tag) {
        while (parent.firstChild) {
          parent.parentNode.insertBefore(parent.firstChild, parent);
        }
        parent.parentNode.removeChild(parent);
      }
    },

    // Apply block formatting (headings, preformatted)
    applyBlockFormat: function (tag) {
      var sel = window.getSelection();
      if (!sel.rangeCount) return;

      var range = sel.getRangeAt(0);
      var block = document.createElement(tag);
      var commonAncestor = range.commonAncestorContainer;
      var container = commonAncestor.nodeType === Node.TEXT_NODE ? commonAncestor.parentNode : commonAncestor;

      // Find the closest block element
      while (container && container.className !== 'rte-editor' && !['P', 'DIV', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'PRE'].includes(container.tagName)) {
        container = container.parentNode;
      }

      if (container && container.className !== 'rte-editor') {
        var newBlock = block.cloneNode(false);
        newBlock.innerHTML = container.innerHTML;
        container.parentNode.replaceChild(newBlock, container);
      }
    },

    // Insert or unwrap a list
    toggleList: function (listType) {
      var sel = window.getSelection();
      if (!sel.rangeCount) return;

      var range = sel.getRangeAt(0);
      var container = range.commonAncestorContainer;
      if (container.nodeType === Node.TEXT_NODE) {
        container = container.parentNode;
      }

      var tagName = listType === 'ul' ? 'UL' : 'OL';
      var existingList = null;
      var temp = container;

      // Check if already in a list
      while (temp && temp.className !== 'rte-editor') {
        if (temp.tagName === tagName) {
          existingList = temp;
          break;
        }
        temp = temp.parentNode;
      }

      if (existingList) {
        // Remove the list
        while (existingList.firstChild) {
          var item = existingList.firstChild;
          while (item.firstChild) {
            existingList.parentNode.insertBefore(item.firstChild, existingList);
          }
          existingList.parentNode.removeChild(item);
        }
        existingList.parentNode.removeChild(existingList);
      } else {
        // Create a new list
        var list = document.createElement(listType);
        var li = document.createElement('li');
        li.textContent = sel.toString() || 'Item';
        list.appendChild(li);
        range.insertNode(list);
      }
    },

    // Insert a link
    insertLink: function (url) {
      var sel = window.getSelection();
      if (!sel.rangeCount || sel.toString().length === 0) return;

      var range = sel.getRangeAt(0);
      var link = document.createElement('a');
      link.href = url;
      link.textContent = sel.toString();

      try {
        range.deleteContents();
        range.insertNode(link);
      } catch (e) {
        // Fallback
        var fragment = range.extractContents();
        link.appendChild(fragment);
        range.insertNode(link);
      }
    },

    // Remove a link
    removeLink: function () {
      var sel = window.getSelection();
      if (!sel.rangeCount) return;

      var range = sel.getRangeAt(0);
      var container = range.commonAncestorContainer;
      if (container.nodeType === Node.TEXT_NODE) {
        container = container.parentNode;
      }

      var link = container.closest('a');
      if (link) {
        while (link.firstChild) {
          link.parentNode.insertBefore(link.firstChild, link);
        }
        link.parentNode.removeChild(link);
      }
    }
  };

  function createButton(iconText, title, onClick) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rte-btn';
    btn.innerHTML = iconText;
    btn.title = title;
    btn.addEventListener('click', function (e) { e.preventDefault(); onClick(); });
    return btn;
  }

  function buildToolbar(editor) {
    var toolbar = document.createElement('div');
    toolbar.className = 'rte-toolbar';

    toolbar.appendChild(createButton('<b>B</b>', 'Bold (Ctrl/Cmd+B)', function () { RTE.applyInlineFormat('strong'); editor.focus(); }));
    toolbar.appendChild(createButton('<i>I</i>', 'Italic (Ctrl/Cmd+I)', function () { RTE.applyInlineFormat('em'); editor.focus(); }));
    toolbar.appendChild(createButton('<u>U</u>', 'Underline', function () { RTE.applyInlineFormat('u'); editor.focus(); }));
    toolbar.appendChild(createButton('S', 'Strikethrough', function () { RTE.applyInlineFormat('s'); editor.focus(); }));
    toolbar.appendChild(createButton('•', 'Unordered List', function () { RTE.toggleList('ul'); editor.focus(); }));
    toolbar.appendChild(createButton('1.', 'Ordered List', function () { RTE.toggleList('ol'); editor.focus(); }));
    toolbar.appendChild(createButton('Link', 'Insert link', function () {
      var url = prompt('Enter a URL', 'https://');
      if (url) RTE.insertLink(url);
      editor.focus();
    }));
    toolbar.appendChild(createButton('Unlink', 'Remove link', function () { RTE.removeLink(); editor.focus(); }));
    toolbar.appendChild(createButton('H2', 'Heading', function () { RTE.applyBlockFormat('h2'); editor.focus(); }));
    toolbar.appendChild(createButton('Code', 'Preformatted', function () { RTE.applyBlockFormat('pre'); editor.focus(); }));

    return toolbar;
  }


  function convert(textarea) {
    if (textarea.__rteInitialized) return;
    textarea.__rteInitialized = true;

    var wrapper = document.createElement('div');
    wrapper.className = 'rte-wrapper';

    var editor = document.createElement('div');
    editor.className = 'rte-editor';
    editor.contentEditable = 'true';
    editor.innerHTML = textarea.value || '';

    var toolbar = buildToolbar(editor);

    wrapper.appendChild(toolbar);
    wrapper.appendChild(editor);

    textarea.style.display = 'none';
    textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);

    // Ensure the textarea gets updated before form submit
    var form = textarea.form;
    if (form) {
      form.addEventListener('submit', function () {
        textarea.value = editor.innerHTML;
      });
    }

    // Keep textarea updated on blur (helpful for non-form consumers)
    editor.addEventListener('blur', function () {
      textarea.value = editor.innerHTML;
    });

    // Handle keyboard shortcuts: Ctrl/Cmd+B for bold, Ctrl/Cmd+I for italic
    editor.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        RTE.applyInlineFormat('strong');
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
        e.preventDefault();
        RTE.applyInlineFormat('em');
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        // Let browser handle native undo
        return;
      } else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) {
        // Let browser handle native redo
        return;
      }
    });

    // Optional: expose API on the textarea
    textarea._rte = {
      editor: editor,
      toolbar: toolbar,
      getHTML: function () { return editor.innerHTML; },
      setHTML: function (html) { editor.innerHTML = html; textarea.value = html; }
    };

    return textarea._rte;
  }

  // Public initializer: selector or node list
  function initRTE(sel) {
    var nodes;
    if (!sel) nodes = document.querySelectorAll('textarea.rte');
    else if (typeof sel === 'string') nodes = document.querySelectorAll(sel);
    else if (NodeList.prototype.isPrototypeOf(sel) || Array.isArray(sel)) nodes = sel;
    else nodes = [sel];

    nodes = nodes || [];
    for (var i = 0; i < nodes.length; i++) {
      var ta = nodes[i];
      if (ta && ta.tagName && ta.tagName.toLowerCase() === 'textarea') convert(ta);
    }
  }

  // Auto-init on DOM ready for textareas with class 'rte'
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { initRTE(); });
  } else {
    initRTE();
  }

  // expose
  window.initRTE = initRTE;
})();
